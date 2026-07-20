#!/usr/bin/env python3
"""
从飞书拉取文档全文并缓存为 Markdown。

设计要点：
- wiki URL / token 可直接传给 `docs +fetch`，CLI 自动解包底层文档，无需手动分类型。
- 缓存过期判断依据飞书侧 `obj_edit_time`：通过 `wiki spaces get_node` 拿到当前 edit_time，
  与缓存元数据里的 edit_time 比对，一致则直接用缓存，不一致则重新拉取。
- 缓存全文 Markdown，满足深度阅读需求（用户选择：缓存完整文档）。
- 可选 `--offline` 模式：把文档内嵌的图片、附件、视频、画板、表格等资源也下载到本地，
  让缓存文档在无网络环境下仍可完整阅读。

使用方法：
    python scripts/fetch_doc.py <wiki_url_or_node_token> [--force] [--offline]

示例：
    python scripts/fetch_doc.py https://ztgame.feishu.cn/wiki/RWWRwubJ3iWESVkkByAcXT1Qnbg --offline
    python scripts/fetch_doc.py RWWRwubJ3iWESVkkByAcXT1Qnbg --force --offline

输出：
    - stdout: 文档 Markdown 全文（offline 模式下图片 URL 已替换为本地路径）
    - stderr: 状态信息（命中缓存 / 重新拉取 / 标题 / 时间戳）
    - 文件: cache/<node_token>.md 与 cache/<node_token>.meta.json
    - offline 模式下还会生成: cache/assets/<node_token>/*
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# 导入同目录下的离线化辅助模块
sys.path.insert(0, str(Path(__file__).parent))
import offline_assets

LARK_RUNNER = [
    "node",
    "C:/Users/v-wangtengda/AppData/Roaming/npm/node_modules/@larksuite/cli/scripts/run.js",
]

CACHE_DIR = Path(__file__).parent.parent / "cache"


def run_cli(args, cwd=None):
    """执行 lark-cli 命令，返回解析后的 JSON（失败返回 None）"""
    cmd = LARK_RUNNER + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(cwd) if cwd else None,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        print(f"  CLI error: {err[:300]}", file=sys.stderr)
        try:
            return json.loads(result.stdout)
        except Exception:
            return None
    try:
        return json.loads(result.stdout)
    except Exception:
        print(f"  解析 CLI 输出失败: {result.stdout[:200]}", file=sys.stderr)
        return None


def extract_node_token(token_or_url):
    """从 wiki URL 中提取 node_token；若已是 token 直接返回"""
    s = token_or_url.strip()
    if s.startswith("http"):
        part = s.split("/wiki/", 1)[-1] if "/wiki/" in s else s.rstrip("/").split("/")[-1]
        return part.split("?")[0].split("#")[0]
    return s


def get_node_info(node_token):
    """通过 wiki spaces get_node 获取节点信息（标题、obj_edit_time、URL）"""
    data = run_cli([
        "wiki", "spaces", "get_node",
        "--params", json.dumps({"token": node_token}, ensure_ascii=False),
        "--format", "json",
    ])
    if not data or not data.get("ok"):
        return None
    return data.get("data", {}).get("node", {})


def fetch_markdown(node_token):
    """通过 docs +fetch 拉取文档全文 Markdown"""
    data = run_cli([
        "docs", "+fetch",
        "--doc", node_token,
        "--doc-format", "markdown",
        "--format", "json",
    ])
    if not data or not data.get("ok"):
        return None
    return data.get("data", {}).get("document", {}).get("content", "")


def fetch_xml(node_token):
    """通过 docs +fetch 拉取文档 XML 结构（含嵌入资源 token/href）"""
    data = run_cli([
        "docs", "+fetch",
        "--doc", node_token,
        "--doc-format", "xml",
        "--detail", "with-ids",
        "--format", "json",
    ])
    if not data or not data.get("ok"):
        return None
    return offline_assets.extract_xml_content(json.dumps(data))


def read_meta(node_token):
    meta_file = CACHE_DIR / f"{node_token}.meta.json"
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def assets_all_present(meta):
    """检查 offline 模式下记录的所有本地资源文件是否都存在"""
    for asset in meta.get("assets", []):
        local = asset.get("local_abs")
        if not local or not os.path.exists(local):
            return False
        if os.path.getsize(local) == 0:
            return False
    return True


def extension_for_type(obj_type, title=""):
    """根据飞书文档类型返回本地缓存文件扩展名"""
    mapping = {
        "docx": "md",
        "doc": "pdf",
        "sheet": "xlsx",
        "bitable": "xlsx",
        "slides": "pptx",
        "file": "",
    }
    ext = mapping.get(obj_type, "")
    if obj_type == "file" and title:
        # 从原始文件名保留扩展名
        candidate = Path(title).suffix.lstrip(".").lower()
        if candidate:
            ext = candidate
    if not ext:
        ext = "bin"
    return ext


def write_meta(node_token, node, offline=False, assets=None, cache_ext="md"):
    """只写缓存元数据，不覆盖正文文件"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    meta_file = CACHE_DIR / f"{node_token}.meta.json"
    meta = {
        "node_token": node_token,
        "obj_token": node.get("obj_token", ""),
        "obj_type": node.get("obj_type", ""),
        "obj_edit_time": str(node.get("obj_edit_time", "")),
        "space_id": node.get("space_id", ""),
        "title": node.get("title", ""),
        "doc_url": f"https://ztgame.feishu.cn/wiki/{node_token}",
        "fetch_time": datetime.now().isoformat(),
        "offline": offline,
        "assets": assets or [],
        "cache_ext": cache_ext,
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta_file


def write_cache(node_token, content, node, assets=None):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{node_token}.md"
    meta_file = CACHE_DIR / f"{node_token}.meta.json"

    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(content)

    meta = {
        "node_token": node_token,
        "obj_token": node.get("obj_token", ""),
        "obj_type": node.get("obj_type", ""),
        "obj_edit_time": str(node.get("obj_edit_time", "")),
        "space_id": node.get("space_id", ""),
        "title": node.get("title", ""),
        "doc_url": f"https://ztgame.feishu.cn/wiki/{node_token}",
        "fetch_time": datetime.now().isoformat(),
        "offline": bool(assets),
        "assets": assets or [],
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return cache_file


def download_file(obj_token, cache_file):
    """对云盘 file 类型使用 drive +download 下载到本地。

    lark-cli 在 Windows 下对 --output 的绝对路径/含 symlink 路径解析有 bug，
    因此临时切换 cwd 到系统 TEMP 目录，用相对路径下载，再 move 到 cache。
    """
    tmp_dir = tempfile.gettempdir()
    tmp_name = f"feishu_dl_{obj_token[:16]}"
    print(f"  ⬇️ 下载 file: {obj_token[:16]}", file=sys.stderr)
    data = run_cli([
        "drive", "+download",
        "--file-token", obj_token,
        "--output", tmp_name,
        "--overwrite",
    ], cwd=tmp_dir)
    if not data or not data.get("ok"):
        return False, f"下载失败: {(data or {}).get('error')}"

    tmp_path = os.path.join(tmp_dir, tmp_name)
    if os.path.exists(tmp_path):
        shutil.move(tmp_path, cache_file)
        return True, ""
    return False, "未能获取下载文件"


def export_document(obj_type, obj_token, cache_file):
    """对非 docx 文档导出为本地文件（sheet→xlsx, bitable→xlsx, slides→pptx, doc→pdf, file→download）"""
    if obj_type == "file":
        return download_file(obj_token, cache_file)

    mapping = {
        "sheet": ("sheet", "xlsx"),
        "bitable": ("bitable", "xlsx"),
        "slides": ("slides", "pptx"),
        "doc": ("docx", "pdf"),
    }
    if obj_type not in mapping:
        return False, f"不支持的类型 {obj_type}"

    doc_type, ext = mapping[obj_type]
    tmp_dir = tempfile.gettempdir()
    print(f"  ⬇️ 导出 {obj_type} 为 {ext}: {obj_token[:16]}", file=sys.stderr)
    data = run_cli([
        "drive", "+export",
        "--doc-type", doc_type,
        "--file-extension", ext,
        "--token", obj_token,
        "--output-dir", ".",
        "--overwrite",
    ], cwd=tmp_dir)
    if not data or not data.get("ok"):
        return False, f"导出失败: {(data or {}).get('error')}"

    exported = data.get("data", {})
    file_path = exported.get("file_path") or exported.get("file_name")
    if file_path and os.path.exists(os.path.join(tmp_dir, file_path)):
        shutil.move(os.path.join(tmp_dir, file_path), cache_file)
        return True, ""

    file_token = exported.get("file_token")
    if file_token:
        dl = run_cli([
            "drive", "+export-download",
            "--file-token", file_token,
            "--output-dir", ".",
        ], cwd=tmp_dir)
        if dl and dl.get("ok"):
            dl_data = dl.get("data", {})
            dl_path = dl_data.get("file_path") or dl_data.get("file_name")
            if dl_path and os.path.exists(os.path.join(tmp_dir, dl_path)):
                shutil.move(os.path.join(tmp_dir, dl_path), cache_file)
                return True, ""

    return False, "未能获取导出文件"


def main():
    parser = argparse.ArgumentParser(description="从飞书拉取文档并缓存全文")
    parser.add_argument("token_or_url", help="wiki URL 或 node_token")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新拉取，忽略缓存")
    parser.add_argument("--offline", "-o", action="store_true", help="同时下载图片/附件/画板/内嵌表格，实现离线可查看")
    args = parser.parse_args()

    node_token = extract_node_token(args.token_or_url)

    # 获取节点信息（用于标题 + 缓存过期判断）
    node = get_node_info(node_token)
    if node is None:
        print(f"❌ 无法获取节点信息：{node_token}", file=sys.stderr)
        print("   请确认 token 正确且当前身份有访问权限（lark-cli auth login）", file=sys.stderr)
        return 1

    title = node.get("title", node_token)
    obj_type = node.get("obj_type", "")
    current_edit_time = str(node.get("obj_edit_time", ""))

    # 检查缓存（先读元数据确定缓存文件扩展名）
    meta = read_meta(node_token)
    cache_ext = "md"
    if meta:
        cache_ext = meta.get("cache_ext") or extension_for_type(meta.get("obj_type", ""), meta.get("title", ""))
    cache_file = CACHE_DIR / f"{node_token}.{cache_ext}"
    if not args.force and cache_file.exists() and meta:
        edit_time_match = meta.get("obj_edit_time") == current_edit_time
        offline_ok = (not args.offline) or (meta.get("offline") and assets_all_present(meta))
        if edit_time_match and offline_ok:
            print(f"✅ 命中缓存（飞书侧未更新）：{title}", file=sys.stderr)
            print(f"   缓存时间：{meta.get('fetch_time', '')}", file=sys.stderr)
            # docx 缓存是 Markdown 文本，其他类型是二进制导出文件，不要按文本读
            if obj_type == "docx":
                print(cache_file.read_text(encoding="utf-8"))
            else:
                print(f"[📎 {title} 已缓存为本地文件，路径：{cache_file}]")
            return 0
        else:
            reason = "飞书侧有更新" if not edit_time_match else "离线资源缺失/未启用离线缓存"
            print(f"♻️  缓存需要刷新（{reason}），重新拉取：{title}", file=sys.stderr)

    # 非 docx 类型：导出为本地文件
    if obj_type != "docx":
        if obj_type == "mindnote":
            print(f"⚠️ 思维导图（mindnote）暂不支持导出：{title}", file=sys.stderr)
            print(f"   请直接在飞书查看： https://ztgame.feishu.cn/wiki/{node_token}", file=sys.stderr)
            return 1

        print(f"📥 从飞书导出 {obj_type}：{title}...", file=sys.stderr)
        obj_token = node.get("obj_token", node_token)
        cache_ext = extension_for_type(obj_type, title)
        cache_file = CACHE_DIR / f"{node_token}.{cache_ext}"
        success, err = export_document(obj_type, obj_token, cache_file)
        if not success:
            print(f"❌ 导出失败：{err}", file=sys.stderr)
            return 1

        # 对 file/slides/sheet 等导出为本地二进制文件的场景，不写 .md 占位文本，只更新元数据
        write_meta(node_token, node, offline=args.offline, cache_ext=cache_ext)
        print(f"💾 已导出：{cache_file}", file=sys.stderr)
        return 0

    # docx 类型：拉取 Markdown 文本
    print(f"📥 从飞书拉取：{title}...", file=sys.stderr)
    content = fetch_markdown(node_token)
    if content is None:
        print(f"❌ 拉取失败：{title}（类型 {obj_type} 可能不支持 markdown 导出）", file=sys.stderr)
        return 1

    assets = None
    if args.offline:
        print(f"🌐 进入离线模式，下载嵌入资源...", file=sys.stderr)
        xml_content = fetch_xml(node_token)
        if xml_content:
            asset_map = offline_assets.download_assets(xml_content, node_token, CACHE_DIR)
            if asset_map:
                content = offline_assets.rewrite_markdown(content, asset_map, node_token)
                assets = list(asset_map.values())
                print(f"   共下载 {len(assets)} 个资源", file=sys.stderr)
            else:
                print(f"   未发现可下载资源", file=sys.stderr)
        else:
            print(f"   ⚠️ 无法获取 XML 结构，跳过资源下载", file=sys.stderr)

    # 本地化飞书 wiki 文档链接：已缓存目标 → ./<token>.md，便于离线跳转
    content = offline_assets.localize_wiki_links(content, CACHE_DIR)

    written = write_cache(node_token, content, node, assets=assets)
    print(f"💾 已缓存：{written}", file=sys.stderr)
    print(f"📄 标题：{title} · 长度：{len(content)} 字符", file=sys.stderr)
    if assets:
        print(f"📦 离线资源：{len(assets)} 个，位于 cache/assets/{node_token}/", file=sys.stderr)
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
