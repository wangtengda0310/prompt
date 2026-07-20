#!/usr/bin/env python3
"""
更新卡牌项目部 Wiki 知识空间的目录文档。

设计要点：
- 一次递归遍历收集全部节点到扁平列表（node_token / title / obj_type / url / depth / path），
  统计和 Markdown 生成都基于这份列表，避免重复扫描飞书（早期版本递归三遍，慢 3 倍）。
- 遇到瞬时 API 错误（retryable）自动重试，单节点失败记录到 errors 而非中断整棵树。
- 输出层级化 Markdown 到 docs/目录.md，保留统计表 + 完整目录。

使用方法：
    python scripts/update_wiki.py

依赖：
    - lark-cli（node 入口），需已 auth login
    - Python 3.10+
输出：
    - docs/目录.md（层级目录）
    - stderr: 进度与统计
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

SPACE_ID = "7360624756670627842"
LARK_RUNNER = [
    "node",
    "C:/Users/v-wangtengda/AppData/Roaming/npm/node_modules/@larksuite/cli/scripts/run.js",
]

TYPE_LABEL = {
    "docx": "📄文档",
    "sheet": "📊表格",
    "mindnote": "🧠思维导图",
    "bitable": "🗂️多维表格",
    "slides": "📽️幻灯片",
    "file": "📎文件",
}

errors = []


def call_cli(parent_token="", page_token=""):
    """调用 lark-cli wiki nodes list，retryable 错误自动重试 3 次"""
    params = {"space_id": SPACE_ID, "page_size": 50}
    if parent_token:
        params["parent_node_token"] = parent_token
    if page_token:
        params["page_token"] = page_token

    cmd = LARK_RUNNER + [
        "wiki", "nodes", "list",
        "--params", json.dumps(params, ensure_ascii=False),
        "--format", "json",
    ]

    data = None
    for _ in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        try:
            data = json.loads(result.stdout)
        except Exception:
            data = None
        if data and data.get("ok"):
            return data
        if data and data.get("error", {}).get("retryable"):
            time.sleep(1.5)
            continue
        return data
    return data


def fetch_children(parent_token="", path=""):
    """获取某父节点的直接子节点（含分页）；失败记录到 errors 并返回已取到的部分"""
    items = []
    page_token = ""
    while True:
        resp = call_cli(parent_token, page_token)
        if not resp or not resp.get("ok"):
            errors.append({"path": path, "parent_token": parent_token, "error": (resp or {}).get("error")})
            print(f"  !! 获取失败 {path} ({parent_token})", file=sys.stderr)
            break
        data = resp.get("data", {})
        items.extend(data.get("items", []))
        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        if not page_token:
            break
    return items


def collect_all():
    """一次递归遍历，返回扁平节点列表（保留 depth / path 以还原层级）"""
    flat = []

    def walk(parent_token="", depth=0, path=""):
        children = fetch_children(parent_token, path)
        print(f"[d{depth}] n={len(flat)} {path or '<root>'} -> {len(children)}", file=sys.stderr)
        for child in children:
            title = child.get("title", "")
            current_path = (path + " / " + title) if path else title
            flat.append({
                "title": title,
                "obj_type": child.get("obj_type", ""),
                "node_token": child.get("node_token", ""),
                "url": child.get("url", ""),
                "depth": depth,
                "path": current_path,
            })
            if child.get("has_child"):
                walk(child.get("node_token", ""), depth + 1, current_path)

    walk()
    return flat


def render_markdown(flat):
    """基于扁平列表生成层级化 Markdown"""
    lines = []
    lines.append("# 卡牌项目部 Wiki 知识空间目录")
    lines.append("")
    lines.append("> 空间信息：团队空间（team）· 私有（private）· 未发布互联网（closed）")
    lines.append(f"> space_id: `{SPACE_ID}`")
    max_depth = max((n["depth"] for n in flat), default=0) + 1
    lines.append(
        f"> 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f" · 共 **{len(flat)}** 个节点 · 最大层级 {max_depth} 级"
    )
    lines.append("")

    # 类型统计
    counts = {}
    for n in flat:
        counts[n["obj_type"]] = counts.get(n["obj_type"], 0) + 1
    lines.append("## 类型统计")
    lines.append("")
    lines.append("| 类型 | 数量 |")
    lines.append("|---|---|")
    for t, c in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {TYPE_LABEL.get(t, t)} | {c} |")
    lines.append(f"| **合计** | **{len(flat)}** |")
    lines.append("")

    # 完整目录
    lines.append("## 完整目录")
    lines.append("")
    for n in flat:
        indent = "  " * n["depth"]
        label = TYPE_LABEL.get(n["obj_type"], n["obj_type"])
        if n["url"]:
            lines.append(f"{indent}- [{n['title']}]({n['url']}) `{label}`")
        else:
            lines.append(f"{indent}- {n['title']} `{label}`")

    return "\n".join(lines)


def main():
    print("开始递归获取卡牌项目部 Wiki 空间节点...", file=sys.stderr)
    flat = collect_all()

    output_file = Path(__file__).parent.parent / "docs" / "目录.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(render_markdown(flat))

    print(f"\n✅ 目录已更新：{output_file}", file=sys.stderr)
    print(f"📊 节点总数：{len(flat)} · 失败节点：{len(errors)}", file=sys.stderr)
    if errors:
        print("⚠️ 部分节点获取失败（可重跑）：", file=sys.stderr)
        for e in errors[:10]:
            print(f"   - {e['path']} ({e['parent_token']})", file=sys.stderr)
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
