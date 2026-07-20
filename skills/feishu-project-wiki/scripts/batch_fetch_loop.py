#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量拉取指定子空间下未缓存的文档（可含离线资源），节奏控制在每分钟 ≤ --rate 篇。

定位方式：在 docs/目录.md 的缩进树中按 --space-node 标题找到根节点，收集其子树下
所有匹配 --type 类型的节点，跳过已缓存的，按目录顺序分批拉取。

设计要点：
- 默认只拉 📄文档(docx)：当前认证缺少 docs:document.content:read，表格/多维表格/幻灯片
  导出会失败、思维导图不支持导出，跳过这些类型避免浪费配额。可用 --type 覆盖。
- 已缓存判断：cache 目录下存在该 token 的正文缓存文件或 .meta.json 即视为已缓存。
- 节奏：每批 --rate 篇，串行调用 fetch_doc.py；批后若耗时 < 60s 则等待补足，保证长期
  平均 ≤ --rate 篇/分钟；若批耗时已超 60s（离线资源下载慢），立即开下一批（不超速）。
- 失败（含单篇 timeout）记录到失败清单，不自动重试，结束时统一报告。

使用：
    python scripts/batch_fetch_loop.py --dry-run
    python scripts/batch_fetch_loop.py                                  # 默认：策划空间 10篇/分钟 含资源
    python scripts/batch_fetch_loop.py --space-node 牌局战斗 --rate 5
    python scripts/batch_fetch_loop.py --text-only --rate 20
"""

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 定位 skill 根目录（本脚本位于 <skill>/scripts/，父级父级即 skill 根）
SKILL_DIR = Path(__file__).resolve().parent.parent
INDEX_MD = SKILL_DIR / "docs" / "目录.md"
CACHE_DIR = SKILL_DIR / "cache"
FETCH_DOC = SKILL_DIR / "scripts" / "fetch_doc.py"
LOG_FILE = SKILL_DIR / "batch_fetch_loop.log"

PER_DOC_TIMEOUT = 300  # 单篇 fetch（含离线资源下载）超时秒数
INTERVAL = 60.0        # 每批目标间隔（秒）：保证 ≤ --rate 篇/分钟

# 匹配目录.md 的节点行：`{缩进}- [标题](https://ztgame.feishu.cn/wiki/TOKEN) `类型``
LINE_RE = re.compile(
    r'^(?P<indent>\s*)- \[(?P<title>[^\]]+)\]'
    r'\(https://ztgame\.feishu\.cn/wiki/(?P<token>[A-Za-z0-9]+)\)\s*`(?P<type>[^`]+)`'
)


def log(msg):
    """同时输出到 stdout 与日志文件，便于后台运行时追踪。"""
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_subtree_docs(space_node, type_filter):
    """解析目录.md 缩进树，返回 space_node 子树下所有 type_filter 类型节点 [(token, title)]。

    遇到缩进 ≤ 根节点缩进级的节点即视为离开子树，停止收集。
    """
    if not INDEX_MD.exists():
        log(f"❌ 目录文件不存在：{INDEX_MD}")
        return []
    lines = INDEX_MD.read_text(encoding="utf-8").splitlines()
    # 找缩进最小的同名节点（顶层优先）。避免同名子节点误匹配：
    # 例如「会议纪要」既是某空间下的📽️幻灯片子节点(缩进4)、又是顶层📄文档(缩进0)，
    # 取第一个会错抓子节点导致子树收集为空。
    candidates = []
    for i, ln in enumerate(lines):
        m = LINE_RE.match(ln)
        if m and m.group("title") == space_node:
            candidates.append((i, len(m.group("indent"))))
    if not candidates:
        log(f"❌ 未在目录.md 找到节点「{space_node}」")
        return []
    root_idx, root_indent = min(candidates, key=lambda x: x[1])
    docs = []
    for ln in lines[root_idx + 1:]:
        m = LINE_RE.match(ln)
        if not m:
            continue  # 空行或非节点行
        if len(m.group("indent")) <= root_indent:
            break  # 遇到同级或更上层的节点，已离开子树
        if m.group("type") == type_filter:
            docs.append((m.group("token"), m.group("title")))
    return docs


def cached_tokens():
    """返回 cache 目录下已存在缓存的 token 集合（正文文件或 .meta.json）。"""
    done = set()
    if not CACHE_DIR.exists():
        return done
    for p in CACHE_DIR.iterdir():
        if not p.is_file():
            continue
        if p.name.endswith(".meta.json"):
            done.add(p.name[: -len(".meta.json")])
        else:
            done.add(p.stem)  # <token>.md / <token>.xlsx ...
    return done


def fetch_one(token, offline):
    """调用 fetch_doc.py 拉取单篇，offline=True 时附加 --offline，返回 (ok, note)。"""
    extra = ["--offline"] if offline else []
    try:
        r = subprocess.run(
            [sys.executable, str(FETCH_DOC), token] + extra,
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(SKILL_DIR),
            timeout=PER_DOC_TIMEOUT,
        )
        ok = r.returncode == 0
        err = (r.stderr or "").strip()
        note = ""
        for ln in err.splitlines():
            if ln.startswith(("📥", "✅", "♻️", "❌", "💾", "📦")):
                note = ln
        return ok, note or (err[-200:] if err else "(无输出)")
    except subprocess.TimeoutExpired:
        return False, f"timeout({PER_DOC_TIMEOUT}s)"
    except Exception as e:
        return False, f"异常:{e}"


def main():
    parser = argparse.ArgumentParser(description="批量拉取子空间未缓存文档（可含离线资源）")
    parser.add_argument("--space-node", default="策划空间", help="子空间根节点标题（默认：策划空间）")
    parser.add_argument("--rate", type=int, default=10, help="每分钟篇数上限（默认 10），每批拉 rate 篇")
    parser.add_argument("--type", default="📄文档", help="只处理该 emoji 类型节点（默认 📄文档）")
    parser.add_argument("--text-only", action="store_true", help="只缓存正文，不下载离线资源（默认下载资源）")
    parser.add_argument("--dry-run", action="store_true", help="仅解析与统计，不拉取")
    args = parser.parse_args()

    if args.rate < 1:
        sys.exit("❌ --rate 必须 ≥ 1")

    os.environ["PYTHONUTF8"] = "1"
    offline = not args.text_only
    # 每次运行覆盖日志开头，便于追踪本次进度
    LOG_FILE.write_text(
        f"[{datetime.now().isoformat(timespec='seconds')}] 启动 batch_fetch_loop "
        f"(space={args.space_node}, rate={args.rate}/min, type={args.type}, offline={offline})\n",
        encoding="utf-8",
    )

    docs = parse_subtree_docs(args.space_node, args.type)
    done = cached_tokens()
    todo = [(t, ti) for (t, ti) in docs if t not in done]
    log(f"「{args.space_node}」子树 {args.type} 节点总数：{len(docs)}")
    log(f"当前已缓存 token 数：{len(done)}（含其他子空间）")
    log(f"未缓存待拉取：{len(todo)} | 节奏：每批 {args.rate} 篇/分钟 | 离线资源：{'是' if offline else '否'}")

    if args.dry_run:
        log("--dry-run 模式：仅统计，不拉取。退出。")
        return
    if not todo:
        log(f"✅ 「{args.space_node}」{args.type} 已全部缓存，无需拉取。退出。")
        return

    batch_size = args.rate
    round_no = total_ok = total_fail = 0
    fails = []
    while todo:
        round_no += 1
        batch, todo = todo[:batch_size], todo[batch_size:]
        t0 = time.time()
        log(f"===== 第 {round_no} 批 开始（{len(batch)} 篇，剩余 {len(todo)}）=====")
        for token, title in batch:
            ok, note = fetch_one(token, offline)
            tag = "✅" if ok else "❌"
            log(f"  {tag} {title} [{token}] {note}")
            if ok:
                total_ok += 1
            else:
                total_fail += 1
                fails.append((token, title, note))
        elapsed = time.time() - t0
        log(f"===== 第 {round_no} 批 完成：本批 {elapsed:.1f}s，累计 成功 {total_ok} / 失败 {total_fail} =====")
        if todo:
            wait = INTERVAL - elapsed
            if wait > 0:
                log(f"  等待 {wait:.1f}s 维持每分钟 ≤{args.rate} 篇节奏 …")
                time.sleep(wait)
            else:
                log(f"  本批已耗时 {elapsed:.1f}s（>{INTERVAL}s），立即开始下一批")

    log(f"🎉 全部循环结束。累计 成功 {total_ok} / 失败 {total_fail}")
    if fails:
        log("—— 失败清单（可手动 fetch_doc.py <token> --offline --force 重试）——")
        for t, ti, n in fails:
            log(f"  ❌ {ti} [{t}] {n}")


if __name__ == "__main__":
    main()
