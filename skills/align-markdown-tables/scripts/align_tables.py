#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 JetBrains IDE 风格对齐 markdown 表格。

规则（反直觉，故脚本化）：
  - 分隔行 dash 紧贴 |：|---|---|（非 | --- | --- |）
  - 数据行空格 padding：| content |
  - 列宽按字符数对齐（中文算 1，不是显示宽度的 2）
  - 保留 align 标记：:---（左）/ ---:（右）/ :--:（中）/ ---（默认左）
  - 数据行内容按 align 方向（右对齐内容靠右、居中居中）
  - 跳过 ``` 或 ~~~ 代码块内的内容（不误处理代码块里的伪表格）
  - 保留原换行符（\n 或 \r\n）

用法:
  python align_tables.py <file.md> [file2.md ...]   # 原地修改（支持多文件）
  python align_tables.py <dir>                       # 递归处理目录下所有 .md
  python align_tables.py <file> --dry-run            # 只预览将对齐几个表格，不写文件
  cat file.md | python align_tables.py -             # stdin → stdout
"""
import io
import os
import sys


def _parse_align(sep_cell):
    """从分隔单元格解析对齐。返回 (left_colon, right_colon)。"""
    s = sep_cell.strip()
    return (s.startswith(':'), s.endswith(':'))


def _pad_cell(content, colw, align):
    """按 align 方向把 content padding 到 colw 宽度（字符数）。"""
    pad = colw - len(content)
    if pad <= 0:
        return content
    left_c, right_c = align
    if left_c and right_c:        # 居中
        lp = pad // 2
        return ' ' * lp + content + ' ' * (pad - lp)
    elif right_c:                 # 右对齐
        return ' ' * pad + content
    else:                         # 左对齐（含 :--- 和 ---）
        return content + ' ' * pad


def _split_row(ln):
    s = ln.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def _is_separator_row(line):
    cells = _split_row(line)
    return bool(cells) and all(set(c) <= set('-:') and c != '' for c in cells)


def align_table(block):
    """对一个表格块对齐，返回对齐后的行列表。"""
    rows = [_split_row(ln) for ln in block]
    if len(rows) < 2:
        return block
    ncol = max(len(r) for r in rows)
    for r in rows:
        while len(r) < ncol:
            r.append('')
    sep_idx = 1
    # 列宽：跳过分隔行，取各单元格最大字符数
    colw = [0] * ncol
    for c in range(ncol):
        for i, r in enumerate(rows):
            if i == sep_idx:
                continue
            colw[c] = max(colw[c], len(r[c]))
    # align 标记
    sep_cells_orig = rows[sep_idx]
    aligns = [_parse_align(sep_cells_orig[c] if c < len(sep_cells_orig) else '')
              for c in range(ncol)]
    out = []
    for i, r in enumerate(rows):
        if i == sep_idx:
            cells = []
            for c in range(ncol):
                left_c, right_c = aligns[c]
                dashes = '-' * (colw[c] + 2)
                if left_c and right_c:        # 居中 :--:
                    cells.append(':' + dashes[1:-1] + ':')
                elif right_c:                 # 右对齐 ---:
                    cells.append(dashes[:-1] + ':')
                elif left_c:                  # 左对齐显式标记 :---
                    cells.append(':' + dashes[:-1])
                else:                         # 默认左对齐 ---
                    cells.append(dashes)
            out.append('|' + '|'.join(cells) + '|')
        else:
            cells = [_pad_cell(r[c], colw[c], aligns[c]) for c in range(ncol)]
            out.append('| ' + ' | '.join(cells) + ' |')
    return out


def align_text(content):
    """对齐文本中的表格，跳过 fenced code block。返回 (新文本, 表格数)。"""
    nl = '\r\n' if '\r\n' in content else '\n'
    lines = content.split(nl)
    result = []
    i = 0
    count = 0
    in_fence = False
    fence_marker = None
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        # fenced code block 边界（``` 或 ~~~，行首可缩进）
        if stripped[:3] in ('```', '~~~'):
            if not in_fence:
                in_fence = True
                fence_marker = stripped[:3]
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = None
            result.append(line)
            i += 1
            continue
        if in_fence:
            result.append(line)  # 代码块内原样保留
            i += 1
            continue
        # 表格检测（仅非代码块）
        if stripped.startswith('|') and i + 1 < len(lines) and _is_separator_row(lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith('|'):
                j += 1
            result.extend(align_table(lines[i:j]))
            count += 1
            i = j
        else:
            result.append(line)
            i += 1
    return nl.join(result), count


def process_file(path, dry_run=False):
    """处理单个文件。返回 (表格数, 是否有变化)。"""
    with io.open(path, encoding='utf-8') as f:
        content = f.read()
    new_content, count = align_text(content)
    if new_content == content:
        return count, False
    if dry_run:
        return count, True
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)
    return count, True


def expand_paths(paths):
    """展开：目录递归 .md，文件原样（- 跳过）。"""
    files = []
    for p in paths:
        if p == '-':
            continue
        if os.path.isdir(p):
            for root, _, fnames in os.walk(p):
                for fn in sorted(fnames):
                    if fn.endswith('.md'):
                        files.append(os.path.join(root, fn))
        else:
            files.append(p)
    return files


def main():
    argv = sys.argv[1:]
    dry_run = '--dry-run' in argv or '-n' in argv
    argv = [a for a in argv if a not in ('--dry-run', '-n')]
    if not argv:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    if argv == ['-']:
        content = sys.stdin.read()
        new_content, count = align_text(content)
        sys.stdout.write(new_content)
        sys.stderr.write("已对齐 %d 个表格（stdin → stdout）\n" % count)
        return
    files = expand_paths(argv)
    if not files:
        print("未找到 .md 文件", file=sys.stderr)
        sys.exit(1)
    total = 0
    changed = 0
    for path in files:
        count, did = process_file(path, dry_run)
        total += count
        if did:
            changed += 1
            action = "[dry-run] 将对齐" if dry_run else "已对齐"
            print("%s %d 个表格: %s" % (action, count, path))
    tail = "（dry-run，未写入）" if dry_run else ""
    print("合计 %d 个文件、%d 个表格%s" % (changed, total, tail))


if __name__ == '__main__':
    main()
