#!/usr/bin/env python3
"""
飞书文档离线化资源下载辅助模块。

负责解析 docx 导出的 XML，识别并下载图片、附件、视频、画板、内嵌表格/多维表格等嵌入资源，
最终生成一份资源映射表，供 fetch_doc.py 把 Markdown 中的远程链接替换为本地相对路径。
"""

import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

LARK_RUNNER = [
    "node",
    "C:/Users/v-wangtengda/AppData/Roaming/npm/node_modules/@larksuite/cli/scripts/run.js",
]

# 资源下载超时（秒）
DOWNLOAD_TIMEOUT = 120


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
        print(f"  解析 CLI 输出失败: {result.stdout[:300]}", file=sys.stderr)
        return None


def safe_filename(name):
    """生成安全的文件名"""
    if not name:
        return "asset"
    # 保留中英文、数字、下划线、点、横线，其余替换为下划线
    name = re.sub(r'[^\w一-鿿　-〿＀-￯\.\-]', "_", name)
    name = re.sub(r"_+", "_", name).strip("._")
    return name or "asset"


def ensure_dir(path):
    """确保目录存在"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def extract_xml_content(json_text):
    """从 docs +fetch --format json 的原始输出中提取 content 字段。

    飞书返回的 content 字段是 XML 字符串，可能包含未转义的特殊字符，
    导致标准 json.loads 失败。这里先用正则提取 content 字段的原始字符串，
    再做 unicode_escape 解码。
    """
    # 尝试先标准解析
    try:
        data = json.loads(json_text)
        if data.get("ok"):
            return data.get("data", {}).get("document", {}).get("content", "")
    except Exception:
        pass

    # fallback: 正则提取 content 字段
    m = re.search(r'"content":\s*"(.*?)"\s*,\s*"', json_text, re.S)
    if not m:
        return ""
    try:
        raw = json.loads('"' + m.group(1) + '"')
    except Exception:
        try:
            import codecs
            raw = codecs.decode(m.group(1), "unicode_escape")
        except Exception:
            raw = m.group(1)
    return raw


def parse_embeds(xml_content, node_token):
    """解析 XML 内容，返回嵌入资源列表。

    每个资源是一个 dict：
    {
        "type": "image" | "attachment" | "whiteboard" | "sheet" | "bitable",
        "token": "...",      # file_token / whiteboard_token / sheet_token
        "href": "...",       # 临时下载 URL（图片/附件有）
        "name": "...",       # 原始文件名/标题
        "mime": "...",       # MIME 类型（可选）
    }
    """
    assets = []

    # 图片
    for img in re.findall(r"<img[^>]+>", xml_content, re.S):
        token_match = re.search(r'\bsrc=["\']([^"\']+)["\']', img)
        href_match = re.search(r'\bhref=["\']([^"\']+)["\']', img)
        name_match = re.search(r'\bname=["\']([^"\']+)["\']', img)
        mime_match = re.search(r'\bmime=["\']([^"\']+)["\']', img)
        if token_match and href_match:
            assets.append({
                "type": "image",
                "token": token_match.group(1),
                "href": html.unescape(href_match.group(1)),
                "name": safe_filename(name_match.group(1)) if name_match else token_match.group(1),
                "mime": mime_match.group(1) if mime_match else "",
            })

    # 附件/视频（source 标签）
    for src in re.findall(r"<source[^>]+>", xml_content, re.S):
        token_match = re.search(r'\btoken=["\']([^"\']+)["\']', src)
        href_match = re.search(r'\bhref=["\']([^"\']+)["\']', src)
        name_match = re.search(r'\bname=["\']([^"\']+)["\']', src)
        mime_match = re.search(r'\bmime=["\']([^"\']+)["\']', src)
        if token_match and href_match:
            assets.append({
                "type": "attachment",
                "token": token_match.group(1),
                "href": html.unescape(href_match.group(1)),
                "name": safe_filename(name_match.group(1)) if name_match else token_match.group(1),
                "mime": mime_match.group(1) if mime_match else "",
            })

    # 画板
    for wb in re.findall(r"<whiteboard[^>]+>", xml_content, re.S):
        token_match = re.search(r'\btoken=["\']([^"\']+)["\']', wb)
        if token_match:
            assets.append({
                "type": "whiteboard",
                "token": token_match.group(1),
                "href": "",
                "name": f"whiteboard_{token_match.group(1)}",
                "mime": "image/svg+xml",
            })

    # 内嵌电子表格
    for sheet in re.findall(r"<sheet[^>]+>", xml_content, re.S):
        token_match = re.search(r'\btoken=["\']([^"\']+)["\']', sheet)
        if token_match:
            assets.append({
                "type": "sheet",
                "token": token_match.group(1),
                "href": "",
                "name": f"sheet_{token_match.group(1)}",
                "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            })

    # 内嵌多维表格
    for bt in re.findall(r"<bitable[^>]+>", xml_content, re.S):
        token_match = re.search(r'\btoken=["\']([^"\']+)["\']', bt)
        if token_match:
            assets.append({
                "type": "bitable",
                "token": token_match.group(1),
                "href": "",
                "name": f"bitable_{token_match.group(1)}",
                "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            })

    # 去重（按 token）
    seen = set()
    unique = []
    for a in assets:
        key = (a["type"], a["token"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def guess_extension(mime, name, asset_type):
    """根据 MIME/文件名/类型推断扩展名"""
    ext_map = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/svg+xml": "svg",
        "video/mp4": "mp4",
        "video/quicktime": "mov",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/csv": "csv",
        "application/pdf": "pdf",
    }
    if mime and mime.lower() in ext_map:
        return ext_map[mime.lower()]
    # 从文件名推断
    if name and "." in name:
        candidate = Path(name).suffix.lstrip(".").lower()
        if candidate:
            return candidate
    # 按类型默认
    defaults = {
        "image": "png",
        "attachment": "bin",
        "whiteboard": "svg",
        "sheet": "xlsx",
        "bitable": "xlsx",
    }
    return defaults.get(asset_type, "bin")


def download_http(url, dest, timeout=DOWNLOAD_TIMEOUT):
    """用 urllib 直接下载 URL 到 dest，返回是否成功"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) feishu-project-wiki/1.0"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            with open(dest, "wb") as f:
                f.write(resp.read())
        return os.path.getsize(dest) > 0
    except Exception as e:
        print(f"  HTTP 下载失败: {e}", file=sys.stderr)
        return False


def download_via_media_download(token, dest, cwd):
    """fallback：用 docs +media-download 下载资源到当前目录，再移动到 dest"""
    filename = Path(dest).name
    tmp = os.path.join(cwd, filename)
    data = run_cli(["docs", "+media-download", "--token", token, "--output", filename, "--overwrite"], cwd=cwd)
    if data and data.get("ok") and os.path.exists(tmp):
        os.replace(tmp, dest)
        return True
    return False


def download_image_or_attachment(asset, assets_dir, cwd):
    """下载图片或附件，返回本地相对路径（相对 cache 目录）"""
    ext = guess_extension(asset.get("mime", ""), asset.get("name", ""), asset["type"])
    local_name = f"{asset['type']}_{asset['token'][:16]}.{ext}"
    local_path = assets_dir / local_name
    rel_path = f"assets/{assets_dir.name}/{local_name}"

    if local_path.exists() and local_path.stat().st_size > 0:
        return rel_path

    print(f"  ⬇️ 下载 {asset['type']}: {asset.get('name', asset['token'][:16])}", file=sys.stderr)

    # 优先用 href 临时 URL 直接 HTTP 下载
    if asset.get("href"):
        if download_http(asset["href"], local_path):
            return rel_path

    # fallback: docs +media-download
    if download_via_media_download(asset["token"], local_path, cwd):
        return rel_path

    print(f"  ⚠️ 未能下载 {asset['type']} {asset['token']}", file=sys.stderr)
    return None


def download_whiteboard(asset, assets_dir, cwd):
    """导出画板为 SVG。

    lark-cli whiteboard +query 的 --output 必须是当前目录内的相对路径，
    因此先 cd 到 cache 根目录（cwd），让命令输出到当前目录，再移动到 assets 子目录。
    """
    local_name = f"whiteboard_{asset['token'][:16]}.svg"
    local_path = assets_dir / local_name
    rel_path = f"assets/{assets_dir.name}/{local_name}"

    if local_path.exists() and local_path.stat().st_size > 0:
        return rel_path

    print(f"  ⬇️ 导出 whiteboard: {asset['token'][:16]}", file=sys.stderr)
    # 先尝试 svg
    tmp_svg = os.path.join(cwd, local_name)
    data = run_cli([
        "whiteboard", "+query",
        "--whiteboard-token", asset["token"],
        "--output_as", "svg",
        "--output", ".",
        "--overwrite",
    ], cwd=cwd)
    if data and data.get("ok") and os.path.exists(tmp_svg):
        os.replace(tmp_svg, local_path)
        return rel_path

    # fallback: image
    local_name_img = f"whiteboard_{asset['token'][:16]}.png"
    local_path_img = assets_dir / local_name_img
    rel_path_img = f"assets/{assets_dir.name}/{local_name_img}"
    tmp_img = os.path.join(cwd, local_name_img)
    data = run_cli([
        "whiteboard", "+query",
        "--whiteboard-token", asset["token"],
        "--output_as", "image",
        "--output", ".",
        "--overwrite",
    ], cwd=cwd)
    if data and data.get("ok") and os.path.exists(tmp_img):
        os.replace(tmp_img, local_path_img)
        return rel_path_img

    print(f"  ⚠️ 未能导出 whiteboard {asset['token']}", file=sys.stderr)
    return None


def export_sheet_or_bitable(asset, assets_dir, cwd):
    """导出内嵌 sheet/bitable 为 xlsx"""
    ext = "xlsx"
    local_name = f"{asset['type']}_{asset['token'][:16]}.{ext}"
    local_path = assets_dir / local_name
    rel_path = f"assets/{assets_dir.name}/{local_name}"

    if local_path.exists() and local_path.stat().st_size > 0:
        return rel_path

    print(f"  ⬇️ 导出 {asset['type']}: {asset['token'][:16]}", file=sys.stderr)
    data = run_cli([
        "drive", "+export",
        "--doc-type", asset["type"],
        "--file-extension", "xlsx",
        "--token", asset["token"],
        "--output-dir", cwd,
        "--overwrite",
    ], cwd=cwd)
    if not data or not data.get("ok"):
        print(f"  ⚠️ 导出失败 {asset['type']} {asset['token']}", file=sys.stderr)
        return None

    # drive +export 异步完成，data 里通常有 file_token 或 job_id；
    # 这里简化：返回的 data 中若包含 file_path/file_name 则直接用
    exported = data.get("data", {})
    file_path = exported.get("file_path") or exported.get("file_name")
    if file_path and os.path.exists(os.path.join(cwd, file_path)):
        os.replace(os.path.join(cwd, file_path), local_path)
        return rel_path

    # 如果有 file_token，需要 +export-download
    file_token = exported.get("file_token")
    if file_token:
        dl = run_cli([
            "drive", "+export-download",
            "--file-token", file_token,
            "--output-dir", cwd,
        ], cwd=cwd)
        if dl and dl.get("ok"):
            dl_data = dl.get("data", {})
            dl_path = dl_data.get("file_path") or dl_data.get("file_name")
            if dl_path and os.path.exists(os.path.join(cwd, dl_path)):
                os.replace(os.path.join(cwd, dl_path), local_path)
                return rel_path

    print(f"  ⚠️ 未能获取导出文件 {asset['type']} {asset['token']}", file=sys.stderr)
    return None


def export_non_docx(obj_type, obj_token, dest_path, cwd):
    """对非 docx 文档（sheet/bitable/slides）导出为本地文件"""
    mapping = {
        "sheet": ("sheet", "xlsx"),
        "bitable": ("bitable", "xlsx"),
        "slides": ("slides", "pptx"),
        "doc": ("docx", "pdf"),
    }
    if obj_type not in mapping:
        return False, f"不支持的类型 {obj_type}"

    doc_type, ext = mapping[obj_type]
    print(f"  ⬇️ 导出 {obj_type} 为 {ext}: {obj_token[:16]}", file=sys.stderr)
    data = run_cli([
        "drive", "+export",
        "--doc-type", doc_type,
        "--file-extension", ext,
        "--token", obj_token,
        "--output-dir", cwd,
        "--overwrite",
    ], cwd=cwd)
    if not data or not data.get("ok"):
        return False, f"导出失败: {(data or {}).get('error')}"

    exported = data.get("data", {})
    file_path = exported.get("file_path") or exported.get("file_name")
    if file_path and os.path.exists(os.path.join(cwd, file_path)):
        os.replace(os.path.join(cwd, file_path), dest_path)
        return True, ""

    file_token = exported.get("file_token")
    if file_token:
        dl = run_cli([
            "drive", "+export-download",
            "--file-token", file_token,
            "--output-dir", cwd,
        ], cwd=cwd)
        if dl and dl.get("ok"):
            dl_data = dl.get("data", {})
            dl_path = dl_data.get("file_path") or dl_data.get("file_name")
            if dl_path and os.path.exists(os.path.join(cwd, dl_path)):
                os.replace(os.path.join(cwd, dl_path), dest_path)
                return True, ""

    return False, "未能获取导出文件"


def download_assets(xml_content, node_token, cache_dir):
    """下载 XML 中所有嵌入资源，返回 asset_map。

    asset_map 结构：
    {
        "原始 URL/token 标识": {
            "type": "image",
            "token": "...",
            "local_rel": "assets/<node_token>/image_xxx.png",
            "local_abs": "C:/.../cache/assets/<node_token>/image_xxx.png",
            "original_href": "https://internal-api-drive-stream...",
        },
        ...
    }
    """
    cache_dir = Path(cache_dir)
    assets_dir = cache_dir / "assets" / node_token
    ensure_dir(assets_dir)

    # 当前工作目录临时设为 cache 根目录，因为 lark-cli 某些命令要求输出在当前目录内
    cwd = cache_dir

    assets = parse_embeds(xml_content, node_token)
    asset_map = {}

    for asset in assets:
        key = asset.get("href") or asset["token"]
        rel = None
        if asset["type"] in ("image", "attachment"):
            rel = download_image_or_attachment(asset, assets_dir, cwd)
        elif asset["type"] == "whiteboard":
            rel = download_whiteboard(asset, assets_dir, cwd)
        elif asset["type"] in ("sheet", "bitable"):
            rel = export_sheet_or_bitable(asset, assets_dir, cwd)

        if rel:
            asset_map[key] = {
                "type": asset["type"],
                "token": asset["token"],
                "local_rel": rel,
                "local_abs": str(cache_dir / rel),
                "original_href": asset.get("href", ""),
                "name": asset.get("name", ""),
                "mime": asset.get("mime", ""),
            }

    return asset_map


def rewrite_markdown(md_content, asset_map, node_token):
    """把 Markdown 中的远程资源 URL 替换为本地相对路径"""
    # 替换 Markdown 图片语法 ![alt](url)
    def replace_img(m):
        alt = m.group(1)
        url = m.group(2)
        if url in asset_map:
            return f"![{alt}]({asset_map[url]['local_rel']})"
        return m.group(0)

    md_content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_img, md_content)

    # 替换 HTML 中的 img/src href（如 <img href="...">、<source href="...">）
    def replace_href(m):
        attr = m.group(1)
        url = m.group(2)
        if url in asset_map:
            return f'{attr}="{asset_map[url]["local_rel"]}"'
        return m.group(0)

    md_content = re.sub(r'(href)="([^"]+)"', replace_href, md_content)

    # 在 whiteboard 占位标签后追加本地文件链接
    for key, info in asset_map.items():
        if info["type"] == "whiteboard":
            wb_tag = f'<whiteboard token="{info["token"]}"></whiteboard>'
            if wb_tag in md_content and info["local_rel"] not in md_content:
                md_content = md_content.replace(
                    wb_tag,
                    f'{wb_tag}\n\n[📎 画板已导出为 SVG（本地）]({info["local_rel"]})\n'
                )
        elif info["type"] in ("sheet", "bitable"):
            # 在正文中若出现该 token 的引用，追加链接
            if info["token"] not in md_content:
                md_content += f"\n\n[📎 {info['type']} 已导出为 Excel（本地）]({info['local_rel']})\n"

    return md_content


# 飞书 wiki 文档链接：[文字](https://ztgame.feishu.cn/wiki/<token> 可选 ?query 或 #hash)
WIKI_LINK_RE = re.compile(r'\[([^\]]*)\]\(https://ztgame\.feishu\.cn/wiki/([A-Za-z0-9]+)([?#][^)\s]*)?\)')


def localize_wiki_links(md_content, cache_dir):
    """把 Markdown 中的飞书 wiki 文档链接本地化为 ./<token>.md 相对路径。

    仅替换目标已缓存（cache/<token>.md 存在）的链接；未缓存保留原 URL，便于离线时
    仍可识别为飞书链接、后续拉取后重跑。block 链接（?blockId / #part）本地化后跳
    目标文档顶部，丢 block 锚点（本地 .md 无 block 级锚点）。
    """
    cache_dir = Path(cache_dir)

    def repl(m):
        label, tok = m.group(1), m.group(2)
        if (cache_dir / f"{tok}.md").exists():
            return f"[{label}](./{tok}.md)"
        return m.group(0)

    return WIKI_LINK_RE.sub(repl, md_content)
