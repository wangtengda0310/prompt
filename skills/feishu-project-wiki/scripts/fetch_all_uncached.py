#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性补拉目录.md 里所有未缓存的 📄文档（全空间，含根节点）。

用于补 batch_fetch_loop 的遗漏：根节点本身（batch 只拉子树不含根）+ 同名子节点
导致 parse 失败的空间（如「会议纪要」）。扫描全空间📄、未缓存的逐个 fetch_doc --offline。

使用：
    python scripts/fetch_all_uncached.py            # 正式补拉
    python scripts/fetch_all_uncached.py --dry-run  # 仅统计
"""
import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SKILL_DIR / "cache"
FETCH_DOC = SKILL_DIR / "scripts" / "fetch_doc.py"
INDEX_MD = SKILL_DIR / "docs" / "目录.md"
LOG_FILE = SKILL_DIR / "fetch_all_uncached.log"

LINE_RE = re.compile(
    r'^(\s*)- \[([^\]]+)\]\(https://ztgame\.feishu\.cn/wiki/([A-Za-z0-9]+)\)\s*`([^`]+)`'
)
BATCH = 10
INTERVAL = 60.0
PER_DOC_TIMEOUT = 600  # 比 batch 的 300 大，应对大文档（如 windows私服）


def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def cached_tokens():
    done = set()
    if not CACHE_DIR.exists():
        return done
    for p in CACHE_DIR.iterdir():
        if not p.is_file():
            continue
        if p.name.endswith(".meta.json"):
            done.add(p.name[: -len(".meta.json")])
        else:
            done.add(p.stem)
    return done


def fetch_one(token):
    try:
        r = subprocess.run(
            [sys.executable, str(FETCH_DOC), token, "--offline"],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(SKILL_DIR), timeout=PER_DOC_TIMEOUT,
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
    p = argparse.ArgumentParser(description="补拉全空间未缓存📄文档")
    p.add_argument("--dry-run", action="store_true", help="仅统计不拉取")
    args = p.parse_args()

    os.environ["PYTHONUTF8"] = "1"
    LOG_FILE.write_text(
        f"[{datetime.now().isoformat(timespec='seconds')}] 启动 fetch_all_uncached\n",
        encoding="utf-8",
    )

    lines = INDEX_MD.read_text(encoding="utf-8").splitlines()
    done = cached_tokens()
    todo = []
    for ln in lines:
        m = LINE_RE.match(ln)
        if m and m.group(4) == "📄文档" and m.group(3) not in done:
            todo.append((m.group(3), m.group(2)))
    log(f"全空间📄文档未缓存: {len(todo)}")

    if args.dry_run:
        log("--dry-run，仅统计。退出。")
        return
    if not todo:
        log("✅ 无未缓存📄文档")
        return

    round_no = ok_n = fail_n = 0
    fails = []
    while todo:
        round_no += 1
        batch, todo = todo[:BATCH], todo[BATCH:]
        t0 = time.time()
        log(f"===== 第{round_no}批 {len(batch)}篇 剩{len(todo)} =====")
        for tok, title in batch:
            ok, note = fetch_one(tok)
            log(f"  {'✅' if ok else '❌'} {title} [{tok}] {note}")
            if ok:
                ok_n += 1
            else:
                fail_n += 1
                fails.append((tok, title, note))
        el = time.time() - t0
        if todo:
            w = INTERVAL - el
            if w > 0:
                log(f"  等{w:.0f}s 维持≤10篇/分钟")
                time.sleep(w)
            else:
                log(f"  本批{el:.0f}s>60s，立即下一批")

    log(f"🎉 完成 成功{ok_n} 失败{fail_n}")
    if fails:
        log("—— 失败清单 ——")
        for t, ti, n in fails:
            log(f"  ❌ {ti}[{t}] {n}")


if __name__ == "__main__":
    main()
