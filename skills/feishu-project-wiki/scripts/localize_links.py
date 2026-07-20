#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把缓存文档里的飞书 wiki 链接本地化为 ./<token>.md 相对路径，实现离线可点击跳转。

扫描 cache/*.md，匹配 [文字](https://ztgame.feishu.cn/wiki/<token>...) 形式的链接：
- 目标文档已缓存（cache/<token>.md 存在）：替换为 [文字](./<token>.md)
- 目标未缓存：保留原 URL，在报告里列出（可后续 fetch_doc 拉取再重跑）

block 链接（?blockId=...&blockType=whiteboard...）本地化后跳目标文档顶部，丢 block 锚点
（本地 .md 无 block 级锚点）。链接文字保留。

使用：
    python scripts/localize_links.py                 # dry-run 统计
    python scripts/localize_links.py --apply         # 实际替换
    python scripts/localize_links.py --only <token>  # 单文档试跑
"""

import argparse
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SKILL_DIR / "cache"

# 匹配 [文字](https://ztgame.feishu.cn/wiki/<token> 可选 ?query 或 #hash)
WIKI_RE = re.compile(r'\[([^\]]*)\]\(https://ztgame\.feishu\.cn/wiki/([A-Za-z0-9]+)([?#][^)\s]*)?\)')


def localize_text(text, cached_tokens):
    """返回 (new_text, hit, miss_tokens)。hit=本地化数，miss_tokens=未缓存目标集合。"""
    hit = 0
    miss = set()

    def repl(m):
        nonlocal hit
        label, tok = m.group(1), m.group(2)
        if tok in cached_tokens:
            hit += 1
            return f"[{label}](./{tok}.md)"
        miss.add(tok)
        return m.group(0)  # 未缓存，保留原 URL

    new = WIKI_RE.sub(repl, text)
    return new, hit, miss


def main():
    p = argparse.ArgumentParser(description="本地化飞书 wiki 链接为 ./<token>.md")
    p.add_argument("--apply", action="store_true", help="实际替换（默认 dry-run）")
    p.add_argument("--only", default="", help="只处理指定 token 的文档（试跑用）")
    args = p.parse_args()

    mds = sorted(CACHE_DIR.glob("*.md"))
    if args.only:
        mds = [m for m in mds if m.stem == args.only]
    cached = {m.stem for m in CACHE_DIR.glob("*.md")}

    total_hit = total_docs = changed_docs = 0
    all_miss = set()
    for md in mds:
        txt = md.read_text(encoding="utf-8")
        new, hit, miss = localize_text(txt, cached)
        if hit or miss:
            total_docs += 1
        if hit:
            changed_docs += 1
            total_hit += hit
            if args.apply and new != txt:
                md.write_text(new, encoding="utf-8")
        all_miss |= miss

    mode = "apply" if args.apply else "dry-run"
    print(f"模式：{mode} | 扫描 {len(mds)} 个 .md")
    print(f"本地化链接：{total_hit} 个 | 涉及文档：{total_docs} | 改写文档：{changed_docs}")
    if all_miss:
        print(f"\n未缓存目标 {len(all_miss)} 个（链接保留原 URL，可 fetch_doc 拉取后重跑）：")
        for t in sorted(all_miss):
            print(f"  {t}")


if __name__ == "__main__":
    main()
