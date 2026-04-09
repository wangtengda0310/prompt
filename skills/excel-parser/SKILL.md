---
name: excel-config-guide
description: |
  Excel 配表专业处理技能 - 用于游戏配置的导航、查询、生成和数据分析。

  **必须使用此技能的场景**：
  - 用户需要查看、浏览、搜索 Excel 配表文件（.xlsx）
  - 用户需要了解配表结构（字段、类型、Sheet 列表）
  - 用户需要预览、筛选、查询 Excel 数据内容
  - 用户需要生成测试用 Excel 文件或模拟数据
  - 用户需要根据条件过滤或分页查询 Excel 行
  - 用户询问"英雄配置"、"技能表"、"卡牌数据"等游戏配置
  - 用户需要查询指定行范围的数据（如"第10-20行"）
  - 用户需要导出、提取、转换 Excel 配表数据

  即使没有明确提及"Excel"或"配表"，当用户需要：
  - 查看表格结构、列定义、字段信息
  - 读取、筛选、查找表格中的数据
  - 创建、生成、构建测试数据文件
  - 处理任何 .xlsx 文件相关的工作

  **适用领域**：游戏策划配表、配置管理、数据分析、测试数据准备

  注意：简单的文件读取可能不会触发此技能 - 请在涉及表格结构理解、数据查询、内容筛选或文件生成时主动使用。
version: 3.0.0
author: Claude Code Team
tags: [excel, game-config, preview, mcp, generate, filter]
---

# Excel 配表处理技能

> 专业处理游戏配置 Excel 文件 - 支持 xlsx 格式的配表导航、数据查询、内容筛选和测试数据生成。

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
### [常见问题](#常见问题) - 注意事项和最佳实践

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

---

## 相关文档

- [MCP 接口使用手册](../../docs/MCP-USAGE.md) - 完整的 MCP 工具文档
- [配表检查规则](../../rain-excel-checker/CLAUDE.md) - 配表校验规则说明
