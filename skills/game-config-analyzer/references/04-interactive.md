# 交互工具

本文档详细说明配表分析的交互工具功能。

## 目录

- [全文搜索](#全文搜索)
- [批量操作](#批量操作)
- [配置模拟器](#配置模拟器)
- [使用示例](#使用示例)

---

## 全文搜索

### 功能概述

跨所有配表搜索特定值，支持：
- **精确匹配** - 完全相等
- **模糊匹配** - 包含关键词
- **正则表达式** - 模式匹配
- **字段限定** - 在特定字段中搜索

### 搜索类型

| 类型 | 语法 | 示例 |
|------|------|------|
| 精确匹配 | `value` 或 `"value"` | `关羽` |
| 模糊匹配 | `contains:value` | `contains:骑` |
| 正则匹配 | `regex:pattern` | `regex:\d{4}-\d{2}-\d{2}` |
| 字段限定 | `field:value` | `Name:关羽` |
| 组合搜索 | `field1:value1 AND field2:value2` | `Type:战令 AND Quality:传说` |

### 实现示例

```python
class ConfigSearcher:
    """配表全文搜索"""

    def __init__(self, scan_result: Dict):
        self.scan_result = scan_result
        self.index = self._build_search_index()

    def _build_search_index(self) -> Dict:
        """构建搜索索引"""
        index = defaultdict(list)

        for file_info in self.scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                data = self._get_sheet_data(sheet_info)

                for row_idx, row in enumerate(data):
                    for field, value in row.items():
                        if value is not None:
                            # 存储值的位置
                            index[str(value)].append({
                                "table": sheet_info["name"],
                                "row": row_idx,
                                "field": field
                            })

        return dict(index)

    def search(self, query: str, search_type: str = "fuzzy") -> List[Dict]:
        """执行搜索"""
        if search_type == "exact":
            return self._exact_search(query)
        elif search_type == "fuzzy":
            return self._fuzzy_search(query)
        elif search_type == "regex":
            return self._regex_search(query)
        elif search_type == "field":
            return self._field_search(query)

    def _fuzzy_search(self, query: str) -> List[Dict]:
        """模糊搜索"""
        results = []

        for key, locations in self.index.items():
            if query.lower() in str(key).lower():
                results.extend(locations)

        return self._deduplicate_results(results)

    def _field_search(self, query: str) -> List[Dict]:
        """字段限定搜索 field:value"""
        try:
            field, value = query.split(":", 1)
        except ValueError:
            return []

        results = []
        for file_info in self.scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                data = self._get_sheet_data(sheet_info)

                for row_idx, row in enumerate(data):
                    if field in row:
                        row_value = str(row[field])
                        if value.lower() in row_value.lower():
                            results.append({
                                "table": sheet_info["name"],
                                "row": row_idx,
                                "field": field,
                                "value": row[field]
                            })

        return results
```

### 搜索输出格式

```json
{
  "query": "关羽",
  "type": "fuzzy",
  "total_matches": 12,
  "matches": [
    {
      "table": "Hero.xlsx",
      "sheet": "Hero",
      "row": 42,
      "field": "Name",
      "value": "关羽"
    },
    {
      "table": "Hero.xlsx",
      "sheet": "Hero",
      "row": 42,
      "field": "Description",
      "value": "三国名将关羽"
    }
  ]
}
```

---

## 批量操作

### 功能概述

对配表进行批量修改：
- **批量添加字段** - 在多个表中添加相同字段
- **批量删除字段** - 删除指定字段
- **批量修改值** - 按条件修改数据
- **批量替换** - 替换特定值

### 操作类型

| 操作 | 说明 | 示例 |
|------|------|------|
| add_field | 添加字段 | 在所有表中添加 Version 字段 |
| remove_field | 删除字段 | 删除所有表中的 Temp 字段 |
| update_value | 修改值 | 将所有 OpenDate 加 1 天 |
| replace_value | 替换值 | 将 `OldValue` 替换为 `NewValue` |

### 实现示例

```python
class BatchOperator:
    """批量操作"""

    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.backup_dir = self.config_dir / ".backup"

    def add_field_to_tables(self, tables: List[str], field_def: Dict) -> Dict:
        """批量添加字段"""
        results = {"success": [], "failed": []}

        # 创建备份
        self._create_backup()

        for table_name in tables:
            file_path = self._find_table_file(table_name)
            if not file_path:
                results["failed"].append({"table": table_name, "reason": "文件未找到"})
                continue

            try:
                wb = openpyxl.load_workbook(file_path)
                sheet = wb.active

                # 添加新列
                new_col = sheet.max_column + 1
                sheet.cell(1, new_col, field_def["chs_name"])
                sheet.cell(2, new_col, field_def["type"])
                sheet.cell(3, new_col, field_def["name"])
                sheet.cell(4, new_col, field_def.get("export", "server"))

                # 填充默认值
                if "default" in field_def:
                    for row in range(5, sheet.max_row + 1):
                        sheet.cell(row, new_col, field_def["default"])

                wb.save(file_path)
                results["success"].append(table_name)

            except Exception as e:
                results["failed"].append({"table": table_name, "reason": str(e)})

        return results

    def remove_field_from_tables(self, tables: List[str], field_name: str) -> Dict:
        """批量删除字段"""
        results = {"success": [], "failed": []}

        self._create_backup()

        for table_name in tables:
            file_path = self._find_table_file(table_name)
            if not file_path:
                results["failed"].append({"table": table_name, "reason": "文件未找到"})
                continue

            try:
                wb = openpyxl.load_workbook(file_path)
                sheet = wb.active

                # 找到字段所在的列
                col_to_delete = None
                for col in range(1, sheet.max_column + 1):
                    if sheet.cell(3, col).value == field_name:
                        col_to_delete = col
                        break

                if col_to_delete:
                    sheet.delete_cols(col_to_delete)
                    wb.save(file_path)
                    results["success"].append(table_name)
                else:
                    results["failed"].append({"table": table_name, "reason": "字段未找到"})

            except Exception as e:
                results["failed"].append({"table": table_name, "reason": str(e)})

        return results

    def update_values_by_condition(self, table: str, condition: Dict, update: Dict) -> Dict:
        """按条件修改值"""
        results = {"updated": 0, "failed": 0}

        file_path = self._find_table_file(table)
        if not file_path:
            return results

        self._create_backup()

        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active

            header_row = 3
            headers = {}
            for col in range(1, sheet.max_column + 1):
                field_name = sheet.cell(header_row, col).value
                if field_name:
                    headers[field_name] = col

            # 遍历数据行
            for row_idx in range(5, sheet.max_row + 1):
                # 检查条件
                match = True
                for field, expected_value in condition.items():
                    if field in headers:
                        actual_value = sheet.cell(row_idx, headers[field]).value
                        if actual_value != expected_value:
                            match = False
                            break

                # 执行更新
                if match:
                    for field, new_value in update.items():
                        if field in headers:
                            sheet.cell(row_idx, headers[field]).value = new_value
                            results["updated"] += 1

            wb.save(file_path)

        except Exception as e:
            results["failed"] += 1

        return results
```

### 操作预览

```python
def preview_batch_operation(self, operation: Dict) -> Dict:
    """预览批量操作结果"""
    preview = {
        "operation": operation["type"],
        "affected_tables": [],
        "affected_rows": 0,
        "changes": []
    }

    # 模拟操作，不实际修改
    if operation["type"] == "update_values":
        for table in operation["tables"]:
            file_path = self._find_table_file(table)
            if file_path:
                # 读取并匹配
                matches = self._find_matching_rows(file_path, operation["condition"])
                preview["affected_tables"].append(table)
                preview["affected_rows"] += len(matches)
                preview["changes"].extend([
                    {"table": table, "row": m["row"], "changes": operation["update"]}
                    for m in matches
                ])

    return preview
```

---

## 配置模拟器

### 功能概述

What-if 分析，预览变更影响：
- **变更预览** - 预览修改后的数据
- **影响评估** - 评估变更对其他表的影响
- **风险评估** - 识别潜在风险
- **回滚方案** - 生成回滚脚本

### 模拟操作

```python
class ConfigSimulator:
    """配置模拟器"""

    def simulate_change(self, table: str, changes: List[Dict], relations: List[Dict]) -> Dict:
        """模拟配置变更"""
        simulation = {
            "changes": changes,
            "direct_impact": [],
            "indirect_impact": [],
            "risks": [],
            "rollback": []
        }

        # 1. 分析直接影响
        for change in changes:
            impact = self._analyze_direct_change(table, change)
            simulation["direct_impact"].append(impact)

        # 2. 分析间接影响（通过关系链）
        impact_analyzer = ImpactAnalyzer()
        indirect = impact_analyzer.analyze_impact(changes, relations)
        simulation["indirect_impact"] = indirect["indirect_impact"]

        # 3. 风险评估
        simulation["risks"] = self._assess_risks(simulation)

        # 4. 生成回滚方案
        simulation["rollback"] = self._generate_rollback(table, changes)

        return simulation

    def _assess_risks(self, simulation: Dict) -> List[Dict]:
        """评估风险"""
        risks = []

        # 检查关键字段修改
        for impact in simulation["direct_impact"]:
            if impact.get("is_primary_key"):
                risks.append({
                    "level": "high",
                    "type": "primary_key_change",
                    "message": f"修改主键 {impact['field']} 可能导致引用失效",
                    "suggestion": "确保所有引用已更新"
                })

        # 检查删除操作
        for impact in simulation["direct_impact"]:
            if impact.get("operation") == "delete":
                risks.append({
                    "level": "high",
                    "type": "data_deletion",
                    "message": f"删除数据可能影响引用表",
                    "suggestion": "先检查并更新引用关系"
                })

        # 检查间接影响
        if len(simulation["indirect_impact"]) > 5:
            risks.append({
                "level": "medium",
                "type": "wide_impact",
                "message": f"变更影响 {len(simulation['indirect_impact'])} 个表",
                "suggestion": "建议进行全面测试"
            })

        return risks

    def _generate_rollback(self, table: str, changes: List[Dict]) -> Dict:
        """生成回滚方案"""
        rollback = {
            "steps": [],
            "sql": [],
            "scripts": []
        }

        for change in changes:
            if change["operation"] == "update":
                rollback["steps"].append(f"恢复 {change['field']} 的原值")
            elif change["operation"] == "delete":
                rollback["steps"].append(f"重新插入被删除的行")
            elif change["operation"] == "insert":
                rollback["steps"].append(f"删除新插入的行")

        # 生成回滚脚本
        rollback["scripts"] = self._generate_rollback_scripts(table, changes)

        return rollback
```

### 模拟报告

```json
{
  "simulation_id": "sim-20250115-001",
  "table": "Hero.xlsx",
  "changes": [
    {
      "operation": "update",
      "field": "OpenDate",
      "row_id": 10804,
      "old_value": "2025-12-15",
      "new_value": "2025-12-16"
    }
  ],
  "direct_impact": [
    {
      "field": "OpenDate",
      "rows_affected": 1,
      "is_primary_key": false
    }
  ],
  "indirect_impact": [
    {
      "table": "Card.xlsx",
      "reason": "引用 Hero.Id",
      "rows_affected": 3
    }
  ],
  "risks": [
    {
      "level": "low",
      "type": "time_constraint",
      "message": "OpenDate 变更可能影响时间约束验证",
      "suggestion": "运行验证确保符合约束"
    }
  ],
  "rollback": {
    "steps": [
      "恢复 Hero.xlsx 第 10804 行的 OpenDate 为 2025-12-15"
    ],
    "scripts": [
      "UPDATE Hero SET OpenDate = '2025-12-15' WHERE Id = 10804"
    ]
  }
}
```

---

## 使用示例

### 全文搜索

```python
searcher = ConfigSearcher(scan_result)

# 精确搜索
results = searcher.search("关羽", "exact")

# 模糊搜索
results = searcher.search("骑", "fuzzy")

# 正则搜索日期
results = searcher.search(r"\d{4}-\d{2}-\d{2}", "regex")

# 字段限定搜索
results = searcher.search("Type:战令", "field")
```

### 批量操作

```python
operator = BatchOperator("/path/to/configs")

# 添加字段
result = operator.add_field_to_tables(
    tables=["Hero.xlsx", "Skill.xlsx"],
    field_def={
        "chs_name": "版本号",
        "type": "int",
        "name": "Version",
        "export": "server",
        "default": 1
    }
)

# 预览操作
preview = operator.preview_batch_operation({
    "type": "update_values",
    "tables": ["Hero.xlsx"],
    "condition": {"Quality": "传说"},
    "update": {"Attack": 999}
})
```

### 配置模拟

```python
simulator = ConfigSimulator()

simulation = simulator.simulate_change(
    table="Hero.xlsx",
    changes=[{
        "operation": "update",
        "field": "OpenDate",
        "row_id": 10804,
        "new_value": "2025-12-16"
    }],
    relations=relations
)

print(f"风险等级: {simulation['risks'][0]['level']}")
print(f"影响表: {len(simulation['indirect_impact'])}")
```
