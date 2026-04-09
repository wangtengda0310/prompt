---
name: excel-config-guide
description: |
  Excel 配表专业处理技能 - 用于游戏配置的导航、查询、生成、数据分析和 Git 版本对比。

  **必须使用此技能的场景**：
  - 用户需要查看、浏览、搜索 Excel 配表文件（.xlsx）
  - 用户需要了解配表结构（字段、类型、Sheet 列表）
  - 用户需要预览、筛选、查询 Excel 数据内容
  - 用户需要生成测试用 Excel 文件或模拟数据
  - 用户需要根据条件过滤或分页查询 Excel 行
  - 用户询问"英雄配置"、"技能表"、"卡牌数据"等游戏配置
  - 用户需要查询指定行范围的数据（如"第10-20行"）
  - 用户需要导出、提取、转换 Excel 配表数据
  - **用户需要对比 Git 提交之间的配表变更**（新增！）
  - **用户需要查看某个 commit 中 Excel 文件的修改内容**（新增！）
  - **用户需要分析 PR 或分支间的配表差异**（新增！）
  - **用户需要查看配表的历史版本变更**（新增！）

  即使没有明确提及"Excel"或"配表"，当用户需要：
  - 查看表格结构、列定义、字段信息
  - 读取、筛选、查找表格中的数据
  - 创建、生成、构建测试数据文件
  - 处理任何 .xlsx 文件相关的工作
  - **对比不同版本的配置文件差异**（新增！）
  - **查看 Git 历史、提交、分支中的配表变更**（新增！）
  - **分析代码提交对配置的影响**（新增！）

  **适用领域**：游戏策划配表、配置管理、数据分析、测试数据准备、版本控制分析

  注意：简单的文件读取可能不会触发此技能 - 请在涉及表格结构理解、数据查询、内容筛选、文件生成或版本对比时主动使用。
version: 4.0.0
author: Claude Code Team
tags: [excel, game-config, preview, mcp, generate, filter, git, diff, version-control]
---

# Excel 配表处理技能

> 专业处理游戏配置 Excel 文件 - 支持 xlsx 格式的配表导航、数据查询、内容筛选、测试数据生成和 Git 版本对比。

## 快速开始

### 前置条件

本技能依赖 `rain-qa-func` MCP 服务，使用前需确保应用已启动：

```bash
cd rain-qa-func
wails3 dev
```

MCP 服务默认运行在 `http://127.0.0.1:8765`

### 配表结构规范

名将杀项目配表遵循统一的 4 行表头结构：

| 行号 | 内容 | 说明 |
|:----:|------|------|
| 第1行 | 中文名称 | 字段的中文说明 |
| 第2行 | 字段类型 | int, string, bool, E#枚举名 |
| 第3行 | 字段名 | 程序使用的英文字段名 |
| 第4行 | 导出标识 | server/client/server/client |

> **重要**: 数据行从第 5 行开始，所有查询和操作都基于此规范。

---

## 📚 功能导航

### [数据浏览](#数据浏览) - 查看配表结构、Sheet 列表、列信息
### [数据查询](#数据查询) - 预览数据、范围查询、条件过滤
### [数据生成](#数据生成) - 创建测试用 Excel 文件
### [游戏配置](#游戏配置) - 获取英雄/技能/卡牌配置
### [Git 版本对比](#git-版本对比) - 对比提交、分支、PR 中的配表变更 ⭐ 新增
### [常见问题](#常见问题) - 注意事项和最佳实践

---

## Git 版本对比

> ⭐ **新功能**: 支持通过 Git 命令对比不同版本的 Excel 配置文件，分析变更历史和影响。

### 功能概览

| 功能 | 说明 | 典型场景 |
|------|------|----------|
| **对比两个 commit** | 查看两个版本间的配表差异 | 分析 PR 的配置变更 |
| **查看单个 commit** | 查看某次提交的配表修改 | Code Review 配置变更 |
| **对比工作区** | 查看未提交的本地修改 | 提交前检查配表变更 |
| **分支对比** | 对比不同分支的配表差异 | 合并前检查配置冲突 |

### Excel 文件识别

支持以下文件类型的变更分析：
- `.xlsx` - Excel 2007+ 格式
- `.xls` - Excel 97-2003 格式
- `.csv` - 逗号分隔值文件

### 变更状态说明

| 状态 | 符号 | 说明 |
|------|------|------|
| Added | `A` | 新增的文件 |
| Modified | `M` | 修改的文件 |
| Deleted | `D` | 删除的文件 |
| Renamed | `R` | 重命名的文件 |

---

### 对比两个 Commit

**场景**: 查看 PR 中修改了哪些配置文件

**命令示例**:
```bash
# 对比两个 commit
git diff <commitA> <commitB> -- '*.xlsx' '*.xls' '*.csv'

# 对比两个分支
git diff main feature/new-hero -- '*.xlsx'

# 对比指定范围
git diff abc123..def456 -- 'config/excel/*.xlsx'
```

**工作流程**:
```
1. 使用 git diff 获取变更文件列表
   git diff <commitA> <commitB> --name-status -- '*.xlsx'

2. 过滤出 Excel 文件
   查找文件扩展名：.xlsx, .xls, .csv

3. 对每个变更文件，提取修改前后的内容
   git show <commitA>:<filePath>  → 旧版本
   git show <commitB>:<filePath>  → 新版本

4. 使用 MCP 工具解析 Excel 内容
   preview_excel_sheet / query_excel_range / filter_excel_data

5. 生成差异对比报告
   表格形式显示变更的单元格
```

**示例输出格式**:
```markdown
## 配表变更报告

### 文件变更统计
- 总计: 15 个文件变更
- 新增: 2 个文件
- 修改: 12 个文件
- 删除: 1 个文件

### 详细变更列表

#### Hero.xlsx (Modified)
**状态**: 修改
**变更行数**: 3 行
**变更摘要**: 新增英雄 "赵云"、"诸葛亮"，调整 "关羽" 的战斗力

| 英雄ID | 英雄名称 | 品质 | 战斗力 | 变更 |
|--------|----------|------|--------|------|
| 1 | 关羽 | 5 | 9500 | ↓ -500 |
| 101 | 赵云 | 5 | 9200 | ✨ 新增 |
| 102 | 诸葛亮 | 5 | 9400 | ✨ 新增 |

#### Card.xlsx (Modified)
**状态**: 修改
**变更行数**: 1 行
**变更摘要**: 调整卡牌 "青龙偃月刀" 的攻击力

| 卡牌ID | 卡牌名称 | 攻击力 | 变更 |
|--------|----------|--------|------|
| 201 | 青龙偃月刀 | 150 | ↑ +10 |

#### NewConfig.xlsx (Added)
**状态**: 新增
**说明**: 新增的配置文件，包含 5 条记录

#### OldConfig.xlsx (Deleted)
**状态**: 删除
**说明**: 该配置文件已从项目中移除
```

---

### 查看单个 Commit

**场景**: 分析某次提交对配表的具体修改

**命令示例**:
```bash
# 查看某个 commit 的变更
git show <commit> -- '*.xlsx'

# 查看某个 commit 的文件列表
git show <commit> --name-status -- '*.xlsx'

# 查看某个 commit 中特定文件的内容
git show <commit>:config/excel/Hero.xlsx
```

**工作流程**:
```
1. 获取 commit 中变更的 Excel 文件列表
   git show <commit> --name-status -- '*.xlsx'

2. 对每个变更文件，获取修改后的内容
   git show <commit>:<filePath>

3. 如果是修改文件，还需要获取修改前的内容
   git show <commit>^:<filePath>

4. 解析并对比两个版本的内容

5. 生成变更报告
```

**示例输出格式**:
```markdown
## Commit abc123 的配表变更分析

**提交信息**: feat: 新增英雄赵云和诸葛亮
**作者**: 张三 <zhangsan@example.com>
**时间**: 2026-04-09 10:30:00

### 变更统计
- 修改文件: 1 个
- 新增行数: 2 行
- 修改行数: 1 行

### Hero.xlsx 变更详情

#### 新增数据
| 英雄ID | 英雄名称 | 品质 | 战斗力 |
|--------|----------|------|--------|
| 101 | 赵云 | 5 | 9200 |
| 102 | 诸葛亮 | 5 | 9400 |

#### 修改数据
| 字段 | 旧值 | 新值 | 变更 |
|------|------|------|------|
| 关羽的战斗力 | 10000 | 9500 | ↓ -500 |
```

---

### 对比当前工作区

**场景**: 查看本地未提交的配表修改

**命令示例**:
```bash
# 对比工作区和 HEAD
git diff -- '*.xlsx' '*.xls' '*.csv'

# 对比工作区和指定 commit
git diff <commit> -- '*.xlsx'

# 查看工作区中 Excel 文件的变更状态
git status -- '*.xlsx'
```

**工作流程**:
```
1. 获取工作区中变更的 Excel 文件
   git diff --name-status -- '*.xlsx'

2. 对每个修改的文件，获取工作区版本和 HEAD 版本
   工作区版本: 直接读取文件
   HEAD 版本: git show HEAD:<filePath>

3. 解析并对比内容

4. 生成本地变更报告
```

**示例输出格式**:
```markdown
## 工作区配表变更（未提交）

### 变更统计
- 待提交的修改: 3 个文件
- 未跟踪的新文件: 1 个文件

### 修改的文件

#### Hero.xlsx (Modified)
**变更摘要**: 修改了 2 个英雄的属性

| 英雄ID | 字段 | 旧值 | 新值 |
|--------|------|------|------|
| 1 | 战斗力 | 9500 | 10000 |
| 2 | 战斗力 | 8800 | 9000 |

#### Skill.xlsx (Modified)
**变更摘要**: 修改了 1 个技能的描述

| 技能ID | 字段 | 旧值 | 新值 |
|--------|------|------|------|
| 501 | 描述 | 对敌人造成伤害 | 对所有敌人造成 150% 伤害 |

### 新增的文件

#### TestConfig.xlsx (Untracked)
**说明**: 新的测试配置文件
**记录数**: 10 条
```

---

### 分支对比

**场景**: 合并前检查两个分支的配表差异

**命令示例**:
```bash
# 对比两个分支
git diff main feature/new-hero -- '*.xlsx'

# 对比分支和当前 HEAD
git diff HEAD origin/main -- '*.xlsx'

# 只查看差异统计
git diff --stat main feature/new-hero -- '*.xlsx'
```

**工作流程**:
```
1. 获取两个分支之间的差异文件列表
   git diff <branchA> <branchB> --name-status -- '*.xlsx'

2. 对每个差异文件，获取两个分支的版本
   branchA 版本: git show <branchA>:<filePath>
   branchB 版本: git show <branchB>:<filePath>

3. 解析并对比内容

4. 生成分支差异报告
```

**示例输出格式**:
```markdown
## 分支差异分析: main vs feature/new-hero

### 差异统计
- 差异文件: 8 个
- main 独有: 1 个
- feature/new-hero 独有: 2 个
- 双方修改: 5 个

### 主要差异

#### feature/new-hero 新增的配置
1. **Hero.xlsx** - 新增 2 个英雄（赵云、诸葛亮）
2. **Skill.xlsx** - 新增 3 个英雄专属技能

#### 双方都修改的配置
1. **Card.xlsx** - main 修改了卡牌属性，feature 也修改了（可能冲突）
2. **Equip.xlsx** - 双方修改了装备配置（需要合并）

### 潜在冲突提醒
⚠️ **Card.xlsx**: 两个分支都修改了同一张卡牌的属性，合并时需要人工确认
```

---

### JSON 格式输出

**场景**: 需要结构化数据进行进一步处理

**输出格式**:
```json
{
  "comparisonType": "commit",
  "source": "abc123",
  "target": "def456",
  "timestamp": "2026-04-09T10:30:00Z",
  "summary": {
    "totalChanges": 15,
    "added": 2,
    "modified": 12,
    "deleted": 1
  },
  "changes": [
    {
      "filePath": "config/excel/Hero.xlsx",
      "status": "modified",
      "changeType": "data",
      "addedRows": 2,
      "modifiedRows": 1,
      "deletedRows": 0,
      "details": {
        "added": [
          {"rowId": "101", "data": {"Name": "赵云", "Quality": 5, "Power": 9200}}
        ],
        "modified": [
          {
            "rowId": "1",
            "field": "Power",
            "oldValue": 10000,
            "newValue": 9500,
            "changeType": "decrease"
          }
        ]
      }
    }
  ]
}
```

---

### 实用 Git 命令速查

| 需求 | 命令 |
|------|------|
| 查看最近的配表变更 | `git log -10 --oneline -- '*.xlsx'` |
| 查看某个文件的修改历史 | `git log --follow -- Hero.xlsx` |
| 查看某次提交修改了哪些配表 | `git show <commit> --name-status -- '*.xlsx'` |
| 对比两个 tag 的配表差异 | `git diff v1.0 v2.0 -- '*.xlsx'` |
| 查看某个 commit 修改的详细内容 | `git show <commit>:config/excel/Hero.xlsx > temp.xlsx` |
| 暂存当前配表修改 | `git stash push -- '*.xlsx'` |
| 恢复暂存的配表修改 | `git stash pop` |

---

### Git Excel 差异分析最佳实践

#### 1. Code Review 时的配表检查

```
收到 PR 后：
1. 获取 PR 的 commit 范围
2. 运行 git diff 分析配表变更
3. 重点关注：
   - 是否修改了核心配置（英雄、技能、卡牌）
   - 数据变更是否符合预期
   - 是否有不相关的配置被误修改
4. 生成变更报告供 Review 使用
```

#### 2. 发布前的配表差异检查

```
准备发布新版本时：
1. 对比 release 分支和 main 分支
2. 检查所有配表变更
3. 验证：
   - 新增配置是否完整
   - 修改配置是否合理
   - 删除配置是否有替代方案
4. 生成发布说明中的配置变更部分
```

#### 3. 问题排查时的历史追溯

```
发现配置问题时：
1. 找到问题引入的时间点
2. 使用 git log 查看该时间段的配表变更
3. 使用 git show 查看具体修改内容
4. 分析问题根因
5. 确定修复方案
```

#### 4. 多人协作时的冲突解决

```
多人修改同一配表时：
1. 各自创建功能分支
2. 定期使用 git diff 对比主分支
3. 提前发现潜在的配置冲突
4. 合并前使用工具对比差异
5. 人工确认冲突解决方案
```

---

### 性能优化建议

**处理大型 Git 历史**：

| 场景 | 推荐方法 |
|------|----------|
| 对比相距很远的 commit | 使用 `git diff --stat` 先看概要，再分析具体文件 |
| 分析大量文件变更 | 先过滤出关键配置文件，再详细分析 |
| 查看某个文件的历史 | 使用 `git log --follow -- <file>` 只看单个文件 |
| 临时提取某个版本 | 使用 `git show` 保存到临时文件，再用 MCP 工具分析 |

**减少 Git 操作开销**：

```bash
# 一次性获取所有变更文件列表
git diff --name-status <commitA> <commitB> -- '*.xlsx' > changes.txt

# 批量处理变更文件
while read status file; do
  # 处理每个文件
done < changes.txt
```

---

## 数据浏览

### 获取配表目录

**工具**: `get_all_excels(dirPath)`

扫描指定目录，返回所有 Excel 文件及其包含的 Sheet 信息。

```json
{
  "filePath": "D:/work/config/excel",
  "sheetName": "Hero",
  "startRow": 10,
  "endRow": 20
}
```

**参数**:
- `dirPath` (必填): Excel 文件目录路径

**返回**: 文件列表，每个文件包含路径和 Sheet 名称数组

---

### 获取 Sheet 列表

**工具**: `get_excel_sheets(filePath)`

获取单个 Excel 文件中的所有 Sheet。

```json
{
  "filePath": "D:/work/config/excel/Hero.xlsx"
}
```

**参数**:
- `filePath` (必填): Excel 文件路径

**返回**: Sheet 信息列表（名称 + 索引）

---

### 获取列信息

**工具**: `get_excel_column_info(filePath, sheetName)`

获取 Sheet 的列定义详情（中文名、类型、字段名、状态）。

```json
{
  "filePath": "D:/work/config/excel/Hero.xlsx",
  "sheetName": "Hero"
}
```

**返回**: 列属性列表

**列状态说明**:
| 状态 | 含义 |
|------|------|
| `NORMAL` | 正常数据列 |
| `COMMENT` | 注释列（类型为 #） |
| `ENUM` | 枚举类型列 |
| `EMPTY` | 空列 |
| `ERROR` | 错误列 |

---

## 数据查询

### 预览数据

**工具**: `preview_excel_sheet(filePath, sheetName, rows?)`

从数据开始（第5行）预览前 N 行。

```json
{
  "filePath": "D:/work/config/excel/Hero.xlsx",
  "sheetName": "Hero",
  "rows": 20
}
```

**参数**:
- `rows` (可选): 预览行数，默认 10

---

### 范围查询

**工具**: `query_excel_range(filePath, sheetName, startRow, endRow?, includeHeader?)`

查询指定行范围的数据，支持分页。

```json
{
  "filePath": "D:/work/config/excel/Hero.xlsx",
  "sheetName": "Hero",
  "startRow": 10,
  "endRow": 20,
  "includeHeader": true
}
```

**参数说明**:
- `startRow` (必填): 起始行号，**从 1 开始**（1 = Excel 第 5 行）
- `endRow` (可选): 结束行号，`0` 或 `-1` 表示到末尾
- `includeHeader` (可选): 是否包含表头行

**典型用法**:
| 需求 | startRow | endRow | 说明 |
|------|----------|--------|------|
| 第 10-20 行 | 10 | 20 | 固定范围 |
| 第 50 行到末尾 | 50 | 0 | 到末尾 |
| 单行查询 | 100 | 100 | startRow = endRow |
| 前 30 行 | 1 | 30 | 从头开始 |

---

### 条件过滤

**工具**: `filter_excel_data(filePath, sheetName, conditions, includeHeader?)`

根据列条件筛选数据，多条件为 AND 关系。

```json
{
  "filePath": "D:/work/config/excel/Hero.xlsx",
  "sheetName": "Hero",
  "conditions": [
    {"columnName": "Quality", "value": "5", "operator": "eq"},
    {"columnName": "Name", "value": "关", "operator": "startsWith"}
  ],
  "includeHeader": true
}
```

**条件结构**:
- `columnName`: 列名（支持字段名或中文名）
- `value`: 匹配值
- `operator`: 操作符
  - `eq` - 等于（默认）
  - `neq` - 不等于
  - `contains` - 包含
  - `startsWith` - 开头
  - `endsWith` - 结尾

---

## 数据生成

### 创建 Excel 文件

**工具**: `create_excel_file(filePath, sheets)`

创建符合项目规范的 Excel 文件，自动生成 4 行表头。

```json
{
  "filePath": "D:/work/test_hero.xlsx",
  "sheets": [
    {
      "sheetName": "Hero",
      "columns": [
        {"chsName": "英雄ID", "fieldType": "int", "fieldName": "Id", "exportTag": "server"},
        {"chsName": "英雄名称", "fieldType": "string", "fieldName": "Name", "exportTag": "server/client"},
        {"chsName": "品质", "fieldType": "int", "fieldName": "Quality", "exportTag": "server"}
      ],
      "dataRows": [
        ["1", "关羽", "5"],
        ["2", "张飞", "4"]
      ]
    }
  ]
}
```

**Sheet 定义结构**:
| 字段 | 说明 | 示例 |
|------|------|------|
| `sheetName` | Sheet 名称 | `"Hero"` |
| `columns` | 列定义数组 | 见下表 |
| `dataRows` | 数据行（二维数组） | `[["1", "关羽"]]` |

**列定义**:
| 字段 | 说明 | 必填 |
|------|------|------|
| `chsName` | 中文名称（表头第1行） | 是 |
| `fieldType` | 字段类型（表头第2行） | 是 |
| `fieldName` | 字段名（表头第3行） | 是 |
| `exportTag` | 导出标识（表头第4行） | 是 |

**支持的字段类型**:
- `int` - 整数
- `string` - 字符串
- `bool` - 布尔值
- `E#枚举名` - 枚举类型（如 `E#ESkillType`）
- `#` - 注释列（fieldName 和 exportTag 留空）

**导出标识**:
- `server` - 仅服务端
- `client` - 仅客户端
- `server/client` - 服务端和客户端

---

## 游戏配置

快速获取游戏数据配置：

| 工具 | 返回数据 |
|------|----------|
| `get_all_hero_cfg()` | 所有英雄配置 |
| `get_all_card_cfg()` | 所有卡牌配置 |
| `get_all_skill_cfg()` | 所有技能配置 |

这些工具无需参数，直接返回完整的配置数据。

---

## 常见问题

### MCP 服务启动失败

**问题**: 调用 MCP 工具时提示服务不可用

**解决**:
```bash
cd rain-qa-func
wails3 dev
```

确保端口 8765 未被占用。

---

### 路径格式问题

**问题**: 文件路径错误

**解决**: Windows 路径使用正斜杠或反斜杠均可：
- ✅ `D:/work/config/excel`
- ✅ `D:\\work\\config\\excel`
- ❌ `D:\work\config\excel` (在 JSON 中需转义)

---

### Sheet 名称大小写

**问题**: Sheet 名称匹配失败

**解决**: Sheet 名称**区分大小写**，需与 Excel 中的完全一致。建议先用 `get_excel_sheets` 查看准确的 Sheet 名称。

---

### 行号计数混乱

**问题**: 查询的行号与 Excel 显示不一致

**解决**:
- 数据行号从 **1** 开始计数
- `startRow=1` 对应 Excel 的**第 5 行**（前 4 行是表头）
- 使用 `includeHeader=true` 可以看到列名帮助定位

---

### 大文件性能问题

**问题**: 处理大文件时响应缓慢

**解决**:
1. 使用 `query_excel_range` 分页查询，避免一次性加载全部数据
2. 使用 `filter_excel_data` 精确筛选，减少返回数据量
3. 预览时限制 `rows` 参数

---

### Git 仓库不在当前目录

**问题**: 需要分析其他 Git 仓库的配表变更

**解决**:
```bash
# 指定 Git 仓库路径
git -C /path/to/repo diff <commitA> <commitB> -- '*.xlsx'

# 或者先切换到目标目录
cd /path/to/repo
git diff <commitA> <commitB> -- '*.xlsx'
```

---

### Git 命令输出乱码

**问题**: Git 输出中文显示为乱码

**解决**:
```bash
# 设置 Git 输出编码
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

---

### Git 提取的 Excel 文件无法直接读取

**问题**: `git show` 输出的不是标准 Excel 文件

**解决**:
```bash
# 将 git show 输出重定向到文件
git show <commit>:config/excel/Hero.xlsx > /tmp/hero_old.xlsx
git show <commit>:config/excel/Hero.xlsx > /tmp/hero_new.xlsx

# 然后使用 MCP 工具分析这两个文件
```

---

## 最佳实践

### 1. 渐进式数据探索

```
1. get_all_excels(dirPath)     → 了解有哪些文件
2. get_excel_sheets(filePath)   → 了解有哪些 Sheet
3. get_excel_column_info(...)   → 了解列结构
4. preview_excel_sheet(...)     → 预览前几行数据
5. query_excel_range / filter   → 获取目标数据
```

### 2. 分页查询大数据集

```json
// 每页 20 行
第 1 页: {"startRow": 1, "endRow": 20}
第 2 页: {"startRow": 21, "endRow": 40}
第 3 页: {"startRow": 41, "endRow": 60}
```

### 3. 条件组合查询

```json
{
  "conditions": [
    {"columnName": "Quality", "value": "5", "operator": "eq"},
    {"columnName": "Name", "value": "关", "operator": "contains"}
  ]
}
```
相当于 SQL: `WHERE Quality = 5 AND Name LIKE '%关%'`

### 4. 生成测试数据模板

生成用于 AI 模拟测试的 Mock 数据：
```json
{
  "filePath": "D:/work/mock_data.xlsx",
  "sheets": [
    {
      "sheetName": "Hero",
      "columns": [
        {"chsName": "英雄ID", "fieldType": "int", "fieldName": "Id", "exportTag": "server"},
        {"chsName": "英雄名称", "fieldType": "string", "fieldName": "Name", "exportTag": "server/client"},
        {"chsName": "品质", "fieldType": "int", "fieldName": "Quality", "exportTag": "server"},
        {"chsName": "战斗力", "fieldType": "int", "fieldName": "Power", "exportTag": "server"}
      ],
      "dataRows": [
        ["1001", "测试英雄A", "5", "9999"],
        ["1002", "测试英雄B", "5", "8888"]
      ]
    }
  ]
}
```

### 5. Git 版本对比工作流

```
1. 确定对比范围
   - PR: 对比 source branch 和 target branch
   - 单次提交: git show <commit>
   - 时间范围: git diff <commitA> <commitB>

2. 获取变更文件列表
   git diff --name-status -- '*.xlsx' '*.xls' '*.csv'

3. 分析关键配置文件
   - 优先查看核心配置（Hero, Card, Skill）
   - 识别新增/修改/删除的记录
   - 对比修改前后的数据差异

4. 生成变更报告
   - 文件变更统计
   - 详细数据对比
   - 潜在影响分析

5. 输出结果
   - Markdown 表格（人类可读）
   - JSON 格式（程序处理）
```

---

## 实战示例

### 示例 1: 查找特定英雄的完整信息

**场景**: 需要查看"关羽"的完整配置信息

```
步骤 1: get_all_excels("D:/work/config/excel")
       → 找到 Hero.xlsx 文件

步骤 2: filter_excel_data(
           filePath: "D:/work/config/excel/Hero.xlsx",
           sheetName: "Hero",
           conditions: [{"columnName": "Name", "value": "关羽", "operator": "contains"}],
           includeHeader: true
       )
       → 返回包含表头和匹配行
```

---

### 示例 2: 生成批量测试数据

**场景**: 为 AI 测试生成 100 个英雄数据

```
构造包含 100 行 dataRows 的 JSON
调用 create_excel_file 生成文件
```

---

### 示例 3: 分页浏览大表

**场景**: Hero 表有 1000+ 行数据，需要分页浏览

```
第 1 页: query_excel_range(..., startRow: 1, endRow: 50)
第 2 页: query_excel_range(..., startRow: 51, endRow: 100)
...依次类推
```

---

### 示例 4: 数据对比

**场景**: 对比两个版本中某个英雄的数据变化

```
版本 A: filter_excel_data(..., conditions: [{"columnName": "Name", "value": "关羽"}])
版本 B: 同上，但使用不同版本的文件路径
对比返回的差异
```

---

### 示例 5: 分析 PR 的配表变更 ⭐ 新增

**场景**: Code Review 时查看 PR #123 修改了哪些配置

```
步骤 1: 获取 PR 的提交范围
        git log origin/main..origin/feature/new-hero --oneline

步骤 2: 获取变更的 Excel 文件列表
        git diff origin/main..origin/feature/new-hero --name-status -- '*.xlsx'

步骤 3: 分析每个变更文件
        - 对每个文件，提取修改前后的版本
        - 使用 MCP 工具解析内容
        - 对比数据差异

步骤 4: 生成变更报告
        - 文件变更统计
        - 详细数据对比
        - 潜在风险提示
```

---

### 示例 6: 追踪配置问题的历史 ⭐ 新增

**场景**: 发现"关羽"的战斗力被错误修改，需要找出问题引入的提交

```
步骤 1: 查看文件修改历史
        git log --follow --oneline -- config/excel/Hero.xlsx

步骤 2: 逐个查看可疑提交
        git show <commit>:config/excel/Hero.xlsx > /tmp/hero.xlsx
        使用 MCP 工具查询关羽的数据

步骤 3: 定位问题提交
        找到战斗力从正确值变为错误值的那次提交

步骤 4: 分析变更原因
        查看该提交的完整信息
        git show <commit>
```

---

### 示例 7: 多分支并行开发时的配置检查 ⭐ 新增

**场景**: 三个功能分支同时修改配表，合并前需要检查冲突

```
步骤 1: 对比三个分支与主分支的差异
        git diff main feature/A --name-status -- '*.xlsx'
        git diff main feature/B --name-status -- '*.xlsx'
        git diff main feature/C --name-status -- '*.xlsx'

步骤 2: 识别潜在冲突
        - 多个分支修改了同一文件
        - 同一行数据被不同分支修改

步骤 3: 生成冲突报告
        - 列出所有冲突点
        - 提供合并建议

步骤 4: 制定合并策略
        - 确定合并顺序
        - 准备冲突解决方案
```

---

## 性能优化建议

### 大文件处理策略

| 数据量 | 推荐方法 | 原因 |
|--------|----------|------|
| < 100 行 | `preview_excel_sheet` | 一次性获取全部 |
| 100-1000 行 | `query_excel_range` 分页 | 按需加载 |
| > 1000 行 | `filter_excel_data` 精准筛选 | 只返回需要的数据 |

### 查询优化技巧

1. **优先使用列名而非中文** - 匹配更快
   ```json
   ✅ {"columnName": "Quality", ...}
   ⚠️  {"columnName": "品质", ...}
   ```

2. **多条件筛选比分别查询更高效**
   ```json
   ✅ 一次查询多个条件
   ❌ 多次查询合并结果
   ```

3. **使用范围查询限制返回量**
   ```json
   ✅ { "startRow": 1, "endRow": 10 }
   ❌ { "startRow": 1, "endRow": 10000 }
   ```

### 批量操作建议

当需要处理多个文件时：
```
1. 先调用 get_all_excels 获取文件列表
2. 并行处理多个文件（如果支持）
3. 分别调用 filter 或 query 工具
```

### Git 操作优化技巧

1. **减少 Git 调用次数**
   ```bash
   ✅ 一次性获取所有变更文件
   git diff --name-status <commitA> <commitB> -- '*.xlsx' > files.txt

   ❌ 多次调用 git diff
   git diff <commitA> <commitB> -- file1.xlsx
   git diff <commitA> <commitB> -- file2.xlsx
   ```

2. **使用 --stat 快速概览**
   ```bash
   # 先看概要统计
   git diff --stat <commitA> <commitB> -- '*.xlsx'

   # 再分析具体文件
   git diff <commitA> <commitB> -- important_file.xlsx
   ```

3. **缓存 Git 输出**
   ```bash
   # 将 Git 输出保存到临时文件
   git show <commit>:config.xlsx > /tmp/config.xlsx

   # 后续分析使用临时文件
   # 避免重复调用 git show
   ```

---

## 相关文档

- [MCP 接口使用手册](../../docs/MCP-USAGE.md) - 完整的 MCP 工具文档
- [配表检查规则](../../rain-excel-checker/CLAUDE.md) - 配表校验规则说明
- [Git 工作流规范](../../../../.github/prompt/chinese-git-workflow.md) - Git 使用最佳实践

---

## 更新日志

### v4.0.0 (2026-04-09)
- ⭐ **新增**: Git 版本对比功能
- ⭐ **新增**: 支持对比两个 commit 之间的配表差异
- ⭐ **新增**: 支持查看单个 commit 的配表变更
- ⭐ **新增**: 支持对比当前工作区与指定 commit
- ⭐ **新增**: 支持分支间的配表差异分析
- ⭐ **新增**: 支持多种输出格式（Markdown、JSON）
- ⭐ **新增**: 新增实战示例（PR 分析、问题追溯、冲突检查）
- 📝 **优化**: 更新技能描述，提高 Git 相关任务的触发准确率

### v3.0.0 (2026-03-24)
- 初始版本，支持基本的 Excel 解析和查询功能
