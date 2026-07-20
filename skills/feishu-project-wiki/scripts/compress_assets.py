#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压缩 feishu-project-wiki 缓存的离线图片资源（PNG → WebP），大幅降低磁盘占用。

两种模式：
- 默认 dry-run：仅在内存把每张 PNG 编码成 WebP 测大小，统计预期节省量，不写盘、不改文件。
- --apply：实际转换——生成 .webp、校验可读后删原 .png、同步改对应 .md / .meta.json 里的引用。

安全约定：
- 逐张转换，校验 WebP 可打开且非空才删原 PNG；失败文件保留原状、其引用不改。
- 只处理 PNG（占 assets 92%）。gif/jpg/mp4 不动。
- 引用同步用精确文件名替换（image_XXX.png→image_XXX.webp），不误伤其他 .png 引用。

依赖：Pillow（含 WebP 编码）。本机 py(3.14) 已装 Pillow 12.3.0 + webp_enc。

使用：
    python scripts/compress_assets.py                          # dry-run 统计预期节省
    python scripts/compress_assets.py --apply --only <token>   # 单文档试跑验证
    python scripts/compress_assets.py --apply                  # 全量执行
    python scripts/compress_assets.py --quality 80 --method 6  # 调质量/压缩力度
"""

import argparse
import io
import json
import sys
from pathlib import Path

from PIL import Image, features

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SKILL_DIR / "cache"
ASSETS_DIR = CACHE_DIR / "assets"


def fmt_mb(n):
    return f"{n / 1024 / 1024:.2f} MB"


def decide_mode(img):
    """原图含透明则 RGBA，否则 RGB——保留透明又避免无谓 alpha 通道膨胀。"""
    if img.mode in ("RGBA", "LA") or "transparency" in img.info:
        return "RGBA"
    return "RGB"


def encode_webp_to_buf(png_path, quality, method):
    """编码到内存测大小（dry-run 用），返回 (png_size, webp_size)。"""
    png_size = png_path.stat().st_size
    with Image.open(png_path) as img:
        img.load()
        mode = decide_mode(img)
        if img.mode != mode:
            img = img.convert(mode)
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=quality, method=method)
    return png_size, buf.tell()


def convert_png_to_webp(png_path, quality, method):
    """实际转换：写 .webp、校验头可读且非空，返回 (webp_path, webp_size)。失败抛异常，不删原文件。"""
    webp_path = png_path.with_suffix(".webp")
    with Image.open(png_path) as img:
        img.load()
        mode = decide_mode(img)
        if img.mode != mode:
            img = img.convert(mode)
        img.save(webp_path, format="WEBP", quality=quality, method=method)
    with Image.open(webp_path) as v:  # 校验生成的 webp 完整可读
        v.verify()
    if webp_path.stat().st_size == 0:
        raise ValueError("webp 大小为 0")
    return webp_path, webp_path.stat().st_size


def run_dryrun(pngs, quality, method, top):
    total_png = total_webp = 0
    per_token = {}
    errors = []
    for i, png in enumerate(pngs, 1):
        try:
            ps, ws = encode_webp_to_buf(png, quality, method)
            total_png += ps
            total_webp += ws
            d = per_token.setdefault(png.parent.name, [0, 0, 0])
            d[0] += ps
            d[1] += ws
            d[2] += 1
        except Exception as e:
            errors.append((str(png), str(e)[:100]))
        if i % 500 == 0:
            print(f"  已处理 {i}/{len(pngs)} …", flush=True)
    saved = total_png - total_webp
    ratio = saved / total_png * 100 if total_png else 0
    print("\n========== 预期统计 ==========")
    print(f"PNG 原始总大小 : {fmt_mb(total_png)}")
    print(f"WebP 预期总大小: {fmt_mb(total_webp)}")
    print(f"预期节省       : {fmt_mb(saved)}  ({ratio:.1f}%)")
    if total_png:
        print(f"平均压缩率     : WebP/PNG = {total_webp / total_png:.3f}")
    print(f"\n===== 节省最多的 Top {top} 文档 =====")
    ranked = sorted(per_token.items(), key=lambda kv: kv[1][0] - kv[1][1], reverse=True)[:top]
    for token, (ps, ws, c) in ranked:
        print(f"  {fmt_mb(ps - ws):>10}  {token}  ({c} 张, {fmt_mb(ps)} → {fmt_mb(ws)})")
    if errors:
        print(f"\n⚠️ {len(errors)} 个失败：")
        for f, e in errors[:5]:
            print(f"  {f}: {e}")
    print("\n（dry-run：未修改任何文件。确认后用 --apply 执行，建议先 --apply --only <token> 试跑。）")


def run_apply(pngs, quality, method, only_token, limit_tokens):
    by_token = {}
    for png in pngs:
        by_token.setdefault(png.parent.name, []).append(png)
    tokens = list(by_token.keys())
    if only_token:
        tokens = [t for t in tokens if t == only_token]
    if limit_tokens:
        tokens = tokens[:limit_tokens]
    target = sum(len(by_token[t]) for t in tokens)
    print(f"apply：{len(tokens)} 个文档 / {target} 张 PNG | quality={quality} method={method}")

    converted = {}  # token -> [(old_basename, new_basename)]
    total_png = total_webp = 0
    errors = []
    done = 0
    for token in tokens:
        conv = []
        for png in by_token[token]:
            try:
                png_size = png.stat().st_size
                webp_path, webp_size = convert_png_to_webp(png, quality, method)
                png.unlink()  # 校验通过才删原 PNG
                conv.append((png.name, webp_path.name))
                total_png += png_size
                total_webp += webp_size
            except Exception as e:
                errors.append((str(png), str(e)[:120]))
            done += 1
            if done % 200 == 0:
                print(f"  已转换 {done}/{target} …", flush=True)
        if conv:
            converted[token] = conv

    # 引用同步：精确文件名替换 .md 与 .meta.json
    sync_md = sync_meta = 0
    for token, convs in converted.items():
        md = CACHE_DIR / f"{token}.md"
        if md.exists():
            txt = md.read_text(encoding="utf-8")
            orig = txt
            for old_bn, new_bn in convs:
                txt = txt.replace(old_bn, new_bn)
            if txt != orig:
                md.write_text(txt, encoding="utf-8")
                sync_md += 1
        meta = CACHE_DIR / f"{token}.meta.json"
        if meta.exists():
            data = json.loads(meta.read_text(encoding="utf-8"))
            changed = False
            for a in data.get("assets", []):
                lr = a.get("local_rel", "")
                la = a.get("local_abs", "")
                for old_bn, new_bn in convs:
                    if old_bn in lr:
                        lr = a["local_rel"] = lr.replace(old_bn, new_bn)
                        changed = True
                    if old_bn in la:
                        la = a["local_abs"] = la.replace(old_bn, new_bn)
                        changed = True
                if a.get("mime") == "image/png" and lr.endswith(".webp"):
                    a["mime"] = "image/webp"
                    changed = True
            if changed:
                meta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                sync_meta += 1

    conv_count = sum(len(c) for c in converted.values())
    saved = total_png - total_webp
    print("\n========== 转换完成 ==========")
    print(f"转换成功：{conv_count} 张")
    if total_png:
        print(f"PNG：{fmt_mb(total_png)} → WebP：{fmt_mb(total_webp)}，节省 {fmt_mb(saved)} ({saved / total_png * 100:.1f}%)")
    print(f"引用同步：.md {sync_md} 个 / .meta.json {sync_meta} 个")
    if errors:
        print(f"\n⚠️ {len(errors)} 个失败（原 PNG 保留、引用未改）：")
        for f, e in errors[:10]:
            print(f"  {f}: {e}")


def main():
    p = argparse.ArgumentParser(description="压缩缓存离线图片 PNG→WebP")
    p.add_argument("--quality", type=int, default=85, help="WebP 质量 1-100（默认 85）")
    p.add_argument("--method", type=int, default=4, help="WebP method 0-6（默认 4，越大压缩越好越慢）")
    p.add_argument("--apply", action="store_true", help="实际执行（默认 dry-run 仅统计）")
    p.add_argument("--only", default="", help="apply 时只处理指定 token（试跑验证用）")
    p.add_argument("--limit", type=int, default=0, help="apply 时只处理前 N 个文档（0=全部）")
    p.add_argument("--top", type=int, default=10, help="dry-run 显示节省最多的前 N 个文档")
    args = p.parse_args()

    if not features.check("webp"):
        sys.exit("❌ Pillow 不支持 WebP 编码，请重装含 webp 的 Pillow")
    if not ASSETS_DIR.exists():
        sys.exit(f"❌ assets 目录不存在：{ASSETS_DIR}")

    pngs = [x for x in sorted(CACHE_DIR.rglob("*.png")) if x.suffix.lower() == ".png"]  # 扫整个 cache：含 assets/<token>/ 与 cache 根的 whiteboard_*.png
    print(f"发现 PNG：{len(pngs)} 个")

    if args.apply:
        run_apply(pngs, args.quality, args.method, args.only, args.limit)
    else:
        print(f"模式：dry-run | quality={args.quality} | method={args.method}")
        run_dryrun(pngs, args.quality, args.method, args.top)


if __name__ == "__main__":
    main()
