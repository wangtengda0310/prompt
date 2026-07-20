# 自适应初始化 — 完整参考文档

> 让 game-config-analyzer 在新机器新项目上零配置使用

## 目录

- [概述](#概述)
- [初始化检测流程](#初始化检测流程)
- [首次初始化步骤](#首次初始化步骤)
- [行角色检测信号](#行角色检测信号)
- [.gameconfig.yaml Schema](#gameconfigyaml-schema)
- [手动编辑指南](#手动编辑指南)
- [异常文件覆盖](#异常文件覆盖)
- [命令行工具](#命令行工具)
- [重新初始化](#重新初始化)
- [优雅降级](#优雅降级)

---

## 概述

自适应初始化解决的核心问题：**不同游戏项目的 Excel 配表格式千差万别**。

硬编码假设（如"4 行表头、字段名在第 3 行"）在新项目上会导致字段提取完全失败。自适应初始化通过采样分析自动探测项目特有的格式参数，持久化到 `.gameconfig.yaml`，后续使用直接读取。

## 初始化检测流程

每次技能触发时，首先执行：

```
检查项目根目录是否存在 .gameconfig.yaml？
  ├─ 存在 → 读取配置，验证有效性，跳过探测
  └─ 不存在 → 进入首次初始化模式（自动执行）
```

## 首次初始化步骤

### 步骤 1: 目录探测

扫描项目目录结构，找到 xlsx 文件集中位置。

检测规则：
- xlsx 文件数最多的子目录为配表目录
- 检查 `enum/` 子目录是否存在（枚举定义）
- 常见目录名：`excel/`, `config/`, `configs/`, `tables/`, `data/`

### 步骤 2: 格式采样

从配表目录中选取 5~10 个代表性文件（按文件大小分层），每个文件读取第一个 Sheet 的前 8 行。

### 步骤 3: 投票确定

对每行的角色进行跨文件投票，确定：
- 字段名在第几行
- 类型声明在第几行
- 中文描述在第几行
- 导出标识在第几行
- 数据从哪一行开始

### 步骤 4: 引用模式发现

扫描所有字段名，统计后缀频率，发现引用命名约定：
- `XxxId` → 单引用（如 `HeroId -> Hero.Id`）
- `XxxIds` → 数组引用
- 其他高频后缀 → 候选引用模式（需人工确认）

### 步骤 5: 生成配置

将所有检测结果写入 `.gameconfig.yaml`，包含置信度评分。

## 行角色检测信号

每行数据会按以下 4 种角色评分，取最高分作为该行角色：

| 角色 | 判定信号 | 评分公式 | 置信度权重 |
|------|---------|---------|-----------|
| `field_name` | 匹配 `^[A-Za-z_][A-Za-z0-9_]*$` 且长度 > 1 | 匹配数 / 非空总数 | 高 |
| `type` | 匹配已知类型（int/string/bool/float）或 `E[A-Z]` 开头或 `[]` 结尾或 `#` 开头 | 匹配数 / 非空总数 | 高 |
| `description` | 含 CJK 字符（`\u4e00-\u9fff`） | 匹配数 / 非空总数 | 中 |
| `export_tag` | 含 `server` 或 `client`（不区分大小写） | 匹配数 / 非空总数 | 高 |

**投票机制**：跨文件统计每行被判定为各角色的次数，取最高票角色。要求票数 > 总采样数 x 30% 才采纳。

## .gameconfig.yaml Schema

完整配置文件结构：

```yaml
# .gameconfig.yaml — Game Config Analyzer 项目配置
# 由自适应初始化自动生成，可手动编辑

version: "1.0"

# === 项目信息 ===
project:
  name: "项目名"           # 默认取目录名
  detected_at: "2026-04-02T..."  # ISO8601 首次检测时间
  detector_version: "1.0"  # 生成此配置的检测器版本

# === 表头格式（核心自适应部分）===
header:
  total_rows: 4             # 表头总行数
  data_start_row: 5         # 数据起始行
  field_name_row: 3         # 字段名所在行
  rows:                     # 每行的角色映射
    1: "description"        # 中文描述
    2: "field_name"         # 字段名
    4: "export_tag"         # 导出标识
  confidence: 0.7           # 检测置信度 0.0~1.0
  samples_used: 10          # 采样文件数
  overrides: {}             # 异常文件覆盖

# === 引用模式 ===
references:
  naming_patterns:
    - pattern: "^(.+)Id$"
      target: "{1}.Id"
      type: "single_reference"
      frequency: 143
    - pattern: "^(.+)Ids$"
      target: "{1}.Id"
      type: "array_reference"
      frequency: 24

  type_patterns:
    - match: "^E[A-Z]"
      reference_type: "enum"
    - match: "^#"
      behavior: "comment_column"
    - match: "\[\]$"
      reference_type: "array"

  discovered_patterns: []

# === Sheet 命名约定 ===
sheet_naming:
  separator: "|"
  use_english_part: true

# === 目录布局 ===
directories:
  excel: "excel"
  enum: null
  output: "docs"
```

## 手动编辑指南

### 最小配置示例

3 行表头（无导出标识行）：
```yaml
version: "1.0"
header:
  total_rows: 3
  data_start_row: 4
  field_name_row: 2
  rows:
    1: "description"
    2: "field_name"
    3: "type"
```

2 行表头（描述+字段名）：
```yaml
version: "1.0"
header:
  total_rows: 2
  data_start_row: 3
  field_name_row: 2
  rows:
    1: "description"
    2: "field_name"
```

自定义引用模式：
```yaml
references:
  naming_patterns:
    - pattern: "^(.+)_id$"
      target: "{1}.id"
      type: "single_reference"
```

## 异常文件覆盖

部分文件可能使用与主流不同的表头格式。通过 `overrides` 字段单独配置：

```yaml
header:
  overrides:
    "ERobotCardFromType_enum.xlsx":
      field_name_row: 1
      total_rows: 2
      data_start_row: 3
    "PeakRankReward_巅峰竞技排名奖励.xlsx":
      field_name_row: 3
      total_rows: 4
      data_start_row: 5
```

匹配规则：文件名精确匹配（不含路径）。

## 命令行工具

```bash
# 自动探测并生成配置
py analyzer.py --init <配表目录>

# 示例
py analyzer.py --init D:/work/mygame/config/excel

# 使用已有配置进行常规分析
py analyzer.py <配表目录>
```

## 重新初始化

删除 `.gameconfig.yaml` 后重新运行 `--init`：

```bash
rm .gameconfig.yaml
py analyzer.py --init <配表目录>
```

何时需要重新初始化：
- 项目新增了大量不同格式的配表文件
- 原有表头格式发生了变更
- 配置文件中 confidence 标记为 low

## 优雅降级

当自动探测的置信度过低（<50%）时，回退到默认假设：

```yaml
header:
  total_rows: 4
  data_start_row: 5
  field_name_row: 3
  rows:
    1: "description"
    2: "type"
    3: "field_name"
    4: "export_tag"
  confidence: 0.3
```

降级原因通常是：
- 采样文件中表头格式不统一
- 文件中空行过多导致行角色评分失准
- 使用了完全非标准的表头结构
