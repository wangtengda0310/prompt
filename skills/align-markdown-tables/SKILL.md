---
name: align-markdown-tables
description: 对齐 markdown（.md）文件中的 GFM 管道表格，消除 JetBrains IDE（IntelliJ IDEA / GoLand / PyCharm / WebStorm）的 "Table is not correctly formatted" 提示。当用户提到 markdown 文档表格的竖线 | 不齐、分隔行横线数量不一、列宽乱、IDE 标黄/黄波浪线/报表格格式警告，或要求"格式化/对齐/美化表格""修掉这些表格提示"、批量处理一个目录下 md 文件的表格时使用。务必在涉及 markdown 表格格式化时触发——即使用户没说"对齐"，只要意图是让 .md 文件里的表格提示消失或更规范（如打开 CLAUDE.md/README 发现有表格波浪线），就应触发。仅限 markdown 表格，不处理 Excel/数据库表/HTML <table>/代码缩进/CSV 转换。
---

# 对齐 Markdown 表格

## 解决什么问题

JetBrains 系 IDE 对 markdown 表格有一套格式检查，不符合就报 `Table is not correctly formatted`（Info/Warning 级，红黄波浪线）。这套标准**不直观**，手算易错，尤其含中文的表格。

## 为什么用脚本而不是手改

三个反直觉的规则，试错代价高（曾出现过"按显示宽度对齐，结果原本不报错的表格也开始报错"的事故）：

1. **分隔行 dash 必须紧贴 `|`**：写成 `|---|---|`，**不能**写成 `| --- | --- |`（带空格）
2. **数据行用空格 padding**：`| content |`
3. **列宽按字符数对齐**（中文字符算 1）——**不是显示宽度**（中文显示占 2）。这是最反直觉的一点。

**实测对照（2026-07-09，把同一张含中文表格分别用三种方式放进 IDE）**：
- 字符数对齐 + 分隔紧贴 → **IDE 无提示** ✓
- 显示宽度对齐 + 分隔紧贴 → **IDE 报 "Table is not correctly formatted"** ✗（视觉好看但 IDE 不认）
- 显示宽度 + 分隔带空格 → IDE 报 ✗

所以**务必用字符数**。中文列视觉上竖线不齐是 IntelliJ 已知的 CJK 表格问题（它按 `String.length()` 检查字符一致性，不按显示宽度）——无法两全，要 IDE 通过就必须接受视觉不齐。**别被"显示宽度视觉对齐"诱惑改用显示宽度**，那会让 IDE 报错（实测验证）。

因为规则反直觉，用本 skill 自带的确定性脚本一次到位，避免反复试错。

## 怎么用

**推荐：文件参数模式**（原地修改，UTF-8 可靠）：

```bash
python <本 skill 目录>/scripts/align_tables.py <要对齐的.md文件>
```

⚠️ **Windows/PowerShell 编码坑**：PowerShell 的 `>` 重定向默认 UTF-16 LE，stdin 管道传中文也可能乱码。**优先用上面的文件参数模式**（脚本内部 `io.open(encoding='utf-8')` 显式读写，不受 shell 编码影响）。若非要用 stdin 管道（`cat file | python align_tables.py -`），务必先设 `PYTHONUTF8=1`（Windows）。

脚本逻辑：
1. 扫描全文，识别所有"连续 `|` 开头行 + 第2行是合法分隔行（只含 `-` `:`）"的表格块
2. 每个表格：按字符数算各列最大宽度 → 数据行 `| content |` 补空格对齐 → 分隔行 dash 紧贴 `|`（数量 = 列宽+2）→ 保留 `:---`（左）/`---:`（右）/`:--:`（中）/`---`（默认左）align 标记
3. 原地写回，打印对齐了几个表格

## 验证

对齐后用 IDE 诊断确认该文件 `Table is not correctly formatted` 清零：

```
mcp__ide__getDiagnostics  (uri 指向该 .md 文件)
```

诊断数组为空即成功。

## 边界与注意

- **只处理标准 GFM 表格**（有分隔行）。没有分隔行的"伪表格"会被跳过。
- **单元格内含字面 `|`**（转义的 `\|`）：脚本按 `|` 分割，会误判列数。遇到这种情况需手动检查或先去掉转义 `|`。
- **不改变任何文字内容**——只调整空格、dash 数量、分隔行紧贴格式。可放心用 `git diff` 核对，应只见空格/dash 变化。
- **幂等**：对已对齐的文件再跑一次不会产生 diff。
- **作用域**：脚本对齐文件内**所有**表格（统一风格）。若只想对齐某几个，自行复制子集处理。
