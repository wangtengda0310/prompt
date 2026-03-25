# 验证引擎

本文档详细说明配表验证引擎的功能和实现。

## 目录

- [数据完整性验证](#数据完整性验证)
- [一致性验证](#一致性验证)
- [业务规则验证](#业务规则验证)
- [错误处理](#错误处理)

---

## 数据完整性验证

### 验证类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 外键引用 | 引用的 ID 必须存在 | Hero.SkillId → Skill.Id |
| 必填字段 | 非空字段必须有值 | Hero.Name 不能为空 |
| 唯一性 | 主键必须唯一 | Hero.Id 必须唯一 |
| 类型检查 | 数据类型必须匹配 | Level 必须是整数 |

### 实现示例

```python
class DataValidator:
    """数据完整性验证器"""

    def validate_referential_integrity(self, scan_result: Dict, relations: List[Dict]) -> List[Dict]:
        """验证外键引用完整性"""
        errors = []

        # 构建 ID 索引
        id_index = self._build_id_index(scan_result)

        # 检查每个引用关系
        for rel in relations:
            source_data = self._get_table_data(rel["source_table"])
            target_ids = id_index.get(rel["target_table"], set())

            for row_idx, row in enumerate(source_data):
                ref_value = row.get(rel["source_field"])
                if ref_value and ref_value not in target_ids:
                    errors.append({
                        "type": "broken_reference",
                        "table": rel["source_table"],
                        "row": row_idx,
                        "field": rel["source_field"],
                        "value": ref_value,
                        "target": f"{rel['target_table']}.{rel['target_field']}",
                        "message": f"引用的 ID {ref_value} 在 {rel['target_table']} 中不存在"
                    })

        return errors

    def validate_required_fields(self, scan_result: Dict) -> List[Dict]:
        """验证必填字段"""
        errors = []

        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                data = self._get_sheet_data(sheet_info)

                for header in sheet_info["headers"]:
                    # 检查是否是必填字段
                    if self._is_required_field(header):
                        for row_idx, row in enumerate(data):
                            if row.get(header["name"]) is None:
                                errors.append({
                                    "type": "missing_required",
                                    "table": sheet_info["name"],
                                    "row": row_idx,
                                    "field": header["name"],
                                    "message": f"必填字段 {header['name']} 为空"
                                })

        return errors

    def validate_uniqueness(self, scan_result: Dict) -> List[Dict]:
        """验证主键唯一性"""
        errors = []

        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                # 找到主键字段（通常是 Id）
                primary_key = self._find_primary_key(sheet_info["headers"])
                if not primary_key:
                    continue

                data = self._get_sheet_data(sheet_info)
                seen_ids = {}

                for row_idx, row in enumerate(data):
                    id_value = row.get(primary_key)
                    if id_value in seen_ids:
                        errors.append({
                            "type": "duplicate_key",
                            "table": sheet_info["name"],
                            "field": primary_key,
                            "value": id_value,
                            "rows": [seen_ids[id_value], row_idx],
                            "message": f"主键 {id_value} 重复出现在行 {seen_ids[id_value]} 和 {row_idx}"
                        })
                    else:
                        seen_ids[id_value] = row_idx

        return errors
```

---

## 一致性验证

### 验证类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 跨表一致性 | 关联数据的一致性 | 卡牌配置与英雄配置一致 |
| 时间顺序 | 时间字段的逻辑关系 | StartTime < EndTime |
| 数值范围 | 数值在合理范围内 | Level ∈ [1, 100] |
| 枚举值 | 枚举值在定义范围内 | Country ∈ ECountry |

### 实现示例

```python
class ConsistencyValidator:
    """一致性验证器"""

    def validate_time_consistency(self, scan_result: Dict) -> List[Dict]:
        """验证时间一致性"""
        errors = []

        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                data = self._get_sheet_data(sheet_info)
                headers = sheet_info["headers"]

                # 查找时间字段
                time_fields = self._find_time_fields(headers)

                # 检查 StartTime < EndTime
                if "StartTime" in time_fields and "EndTime" in time_fields:
                    for row_idx, row in enumerate(data):
                        start = row.get("StartTime")
                        end = row.get("EndTime")

                        if start and end and start >= end:
                            errors.append({
                                "type": "time_order",
                                "table": sheet_info["name"],
                                "row": row_idx,
                                "message": f"StartTime ({start}) 必须小于 EndTime ({end})"
                            })

        return errors

    def validate_enum_values(self, scan_result: Dict) -> List[Dict]:
        """验证枚举值"""
        errors = []

        # 构建枚举值索引
        enum_index = self._build_enum_index(scan_result)

        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                headers = sheet_info["headers"]
                data = self._get_sheet_data(sheet_info)

                for header in headers:
                    # 检查是否是枚举类型字段
                    enum_name = self._parse_enum_type(header.get("type", ""))
                    if enum_name and enum_name in enum_index:
                        valid_values = enum_index[enum_name]

                        for row_idx, row in enumerate(data):
                            value = row.get(header["name"])
                            if value and value not in valid_values:
                                errors.append({
                                    "type": "invalid_enum",
                                    "table": sheet_info["name"],
                                    "row": row_idx,
                                    "field": header["name"],
                                    "value": value,
                                    "valid_values": list(valid_values),
                                    "message": f"枚举值 {value} 不在 {enum_name} 定义中"
                                })

        return errors

    def validate_cross_table_consistency(self, scan_result: Dict, relations: List[Dict]) -> List[Dict]:
        """验证跨表一致性"""
        errors = []

        # 示例：验证英雄的技能引用与技能表的类型一致
        hero_data = self._get_table_data("Hero")
        skill_data = self._get_table_data("Skill")

        for hero in hero_data:
            skill_ids = self._parse_skill_ids(hero.get("Skills", ""))
            for skill_id in skill_ids:
                skill = self._find_skill_by_id(skill_data, skill_id)
                if skill:
                    # 验证技能类型与英雄类型匹配
                    if not self._is_type_compatible(hero, skill):
                        errors.append({
                            "type": "cross_table_inconsistency",
                            "message": f"英雄 {hero['Id']} 的技能 {skill_id} 类型不匹配"
                        })

        return errors
```

---

## 业务规则验证

### 规则引擎

```python
class BusinessRuleValidator:
    """业务规则验证器"""

    def __init__(self):
        self.rules = []

    def add_rule(self, rule: Dict):
        """添加验证规则"""
        self.rules.append(rule)

    def validate(self, scan_result: Dict) -> List[Dict]:
        """执行所有规则验证"""
        errors = []

        for rule in self.rules:
            rule_errors = self._apply_rule(rule, scan_result)
            errors.extend(rule_errors)

        return errors

    def _apply_rule(self, rule: Dict, scan_result: Dict) -> List[Dict]:
        """应用单个规则"""
        errors = []
        rule_type = rule.get("type")

        if rule_type == "conditional":
            errors = self._validate_conditional(rule, scan_result)
        elif rule_type == "range":
            errors = self._validate_range(rule, scan_result)
        elif rule_type == "custom":
            errors = self._validate_custom(rule, scan_result)

        return errors
```

### 规则定义示例

```python
# 规则 1: 战令武将 OpenDate 约束
rule_season_pass_hero = {
    "type": "conditional",
    "name": "战令武将 OpenDate 约束",
    "table": "Hero",
    "condition": "Type == 'SeasonPass'",
    "validations": [
        {
            "field": "OpenDate",
            "rule": "OpenDate >= SeasonPass.StartTime && OpenDate <= SeasonPass.EndTime",
            "message": "战令武将的 OpenDate 必须在战令时间范围内"
        }
    ]
}

# 规则 2: 大将军武将 OpenDate 约束
rule_general_hero = {
    "type": "conditional",
    "name": "大将军武将 OpenDate 约束",
    "table": "Hero",
    "condition": "Type == 'General'",
    "validations": [
        {
            "field": "OpenDate",
            "rule": "OpenDate == ArenaSeason.SeasonStartTime",
            "message": "大将军武将的 OpenDate 必须等于赛季开始时间"
        }
    ]
}

# 规则 3: 等级范围约束
rule_level_range = {
    "type": "range",
    "name": "英雄等级范围",
    "table": "Hero",
    "field": "Level",
    "min": 1,
    "max": 100,
    "message": "英雄等级必须在 1-100 之间"
}
```

### 规则文件格式

```yaml
# validation_rules.yaml
rules:
  - name: 战令武将 OpenDate 约束
    type: conditional
    table: Hero
    condition:
      field: Type
      operator: "=="
      value: SeasonPass
    validations:
      - field: OpenDate
        rule:
          type: time_range
          ref_table: SeasonPass
          start_field: StartTime
          end_field: EndTime
        message: 战令武将的 OpenDate 必须在战令时间范围内

  - name: 大将军武将 OpenDate 约束
    type: conditional
    table: Hero
    condition:
      field: Type
      operator: "=="
      value: General
    validations:
      - field: OpenDate
        rule:
          type: time_equal
          ref_table: ArenaSeason
          ref_field: SeasonStartTime
        message: 大将军武将的 OpenDate 必须等于赛季开始时间

  - name: 英雄等级范围
    type: range
    table: Hero
    field: Level
    min: 1
    max: 100
    message: 英雄等级必须在 1-100 之间
```

---

## 错误处理

### 错误分级

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| 错误 | 严重问题，必须修复 | 阻止导出 |
| 警告 | 潜在问题，建议检查 | 显示警告 |
| 信息 | 提示信息，可选处理 | 记录日志 |

### 错误报告格式

```json
{
  "summary": {
    "total_errors": 15,
    "by_severity": {
      "error": 5,
      "warning": 8,
      "info": 2
    },
    "by_type": {
      "broken_reference": 3,
      "missing_required": 2,
      "time_order": 5,
      "invalid_enum": 3,
      "cross_table_inconsistency": 2
    }
  },
  "errors": [
    {
      "severity": "error",
      "type": "broken_reference",
      "table": "Hero.xlsx",
      "sheet": "Hero",
      "row": 42,
      "field": "SkillId",
      "value": 9999,
      "message": "引用的技能 ID 9999 在 Skill 表中不存在"
    }
  ]
}
```

### 错误修复建议

```python
def suggest_fix(error: Dict) -> str:
    """根据错误类型提供修复建议"""
    error_type = error["type"]

    suggestions = {
        "broken_reference": f"1. 检查引用值 {error['value']} 是否正确\n"
                           f"2. 在 {error['target']} 表中添加对应记录\n"
                           f"3. 或删除此引用",
        "missing_required": f"为 {error['table']} 表第 {error['row']} 行的 {error['field']} 字段填写值",
        "time_order": "确保 StartTime 早于 EndTime",
        "invalid_enum": f"从以下值中选择: {', '.join(error['valid_values'])}",
        "duplicate_key": f"修改或删除重复的 ID {error['value']}"
    }

    return suggestions.get(error_type, "请手动检查此错误")
```

---

## 使用示例

```python
# 创建验证器
validator = ConfigValidator()

# 执行所有验证
results = validator.validate_all(scan_result, relations)

# 输出报告
print(f"验证完成: {results['summary']['total_errors']} 个问题")
print(f"  错误: {results['summary']['by_severity']['error']}")
print(f"  警告: {results['summary']['by_severity']['warning']}")

# 按表分组显示
for table, errors in results['by_table'].items():
    if errors:
        print(f"\n{table}:")
        for error in errors:
            print(f"  [{error['severity'].upper()}] {error['message']}")
            print(f"    建议: {suggest_fix(error)}")
```
