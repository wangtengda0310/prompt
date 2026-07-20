#!/usr/bin/env python3
"""
在本地目录文档（docs/目录.md）中搜索节点。

按关键词匹配标题与层级路径，返回命中节点的标题、类型、层级路径和链接。
纯本地匹配，不访问飞书，因此很快；目录文档由 update_wiki.py 维护。

使用方法：
    python scripts/search_wiki.py <关键词> [关键词2 ...] [--limit N]

匹配规则：
    - 多个关键词为 AND 语义（全部命中路径才算匹配）
    - 大小写不敏感
    - 命中标题本身的结果排在命中路径的结果之前
    - 按层级深度浅的优先（更接近顶层的目录更可能是用户想找的入口）

示例：
    python scripts/search_wiki.py 策划空间
    python scripts/search_wiki.py 服务器 清单
    python scripts/search_wiki.py 测试 --limit 30
"""

import argparse
import re
import sys
from pathlib import Path

DOC_FILE = Path(__file__).parent.parent / "docs" / "目录.md"

# 目录行形如：`    - [标题](url) \`📄文档\``
LINE_RE = re.compile(r"^(?P<indent>\s*)- \[(?P<title>.+?)\]\((?P<url>[^)]+)\)\s*`(?P<label>[^`]+)`")
# 无链接的行：`    - 标题 \`类型\``
LINE_RE_NOURL = re.compile(r"^(?P<indent>\s*)- (?P<title>.+?)\s*`(?P<label>[^`]+)`")


def parse_doc():
    """解析目录文档，返回节点列表，附带每个节点的层级路径（祖先标题链）"""
    if not DOC_FILE.exists():
        print(f"❌ 目录文档不存在：{DOC_FILE}", file=sys.stderr)
        print("   请先运行 scripts/update_wiki.py 生成目录", file=sys.stderr)
        sys.exit(1)

    nodes = []
    ancestors = {}  # depth -> title
    for raw in DOC_FILE.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(raw) or LINE_RE_NOURL.match(raw)
        if not m:
            continue
        indent = m.group("indent")
        depth = len(indent) // 2
        title = m.group("title").strip()
        label = m.group("label").strip()
        url = m.groupdict().get("url", "")

        ancestors[depth] = title
        # 清理更深层的祖先
        for d in list(ancestors.keys()):
            if d > depth:
                del ancestors[d]
        path = " / ".join(ancestors[d] for d in sorted(ancestors) if d <= depth)

        nodes.append({
            "title": title,
            "label": label,
            "url": url,
            "depth": depth,
            "path": path,
        })
    return nodes


def search(nodes, keywords):
    """AND 语义匹配；返回 (命中标题?, depth, node) 排序后的列表"""
    kws = [k.lower() for k in keywords]
    results = []
    for n in nodes:
        title_l = n["title"].lower()
        path_l = n["path"].lower()
        # 全部关键词都要在路径（含标题）中出现
        if all(k in path_l for k in kws):
            title_hit = all(k in title_l for k in kws)
            results.append((0 if title_hit else 1, n["depth"], n))
    results.sort(key=lambda x: (x[0], x[1]))
    return [r[2] for r in results]


def main():
    parser = argparse.ArgumentParser(description="在本地 Wiki 目录中搜索文档")
    parser.add_argument("keywords", nargs="+", help="搜索关键词（多个为 AND 语义）")
    parser.add_argument("--limit", type=int, default=20, help="最多返回结果数（默认 20）")
    args = parser.parse_args()

    nodes = parse_doc()
    results = search(nodes, args.keywords)

    if not results:
        print(f"未找到匹配「{' '.join(args.keywords)}」的文档", file=sys.stderr)
        return 1

    print(f"找到 {len(results)} 个匹配（显示前 {min(args.limit, len(results))} 个）：\n", file=sys.stderr)
    for n in results[:args.limit]:
        loc = n["path"] if n["path"] != n["title"] else "（顶层）"
        if n["url"]:
            print(f"- [{n['title']}]({n['url']}) `{n['label']}`")
            print(f"    位置：{loc}")
        else:
            print(f"- {n['title']} `{n['label']}`")
            print(f"    位置：{loc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
