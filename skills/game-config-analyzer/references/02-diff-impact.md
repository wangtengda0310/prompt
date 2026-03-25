# 差异与影响分析

本文档详细说明配表版本对比和影响分析功能。

## 目录

- [差异分析](#差异分析)
- [影响分析](#影响分析)
- [依赖追溯](#依赖追溯)
- [使用示例](#使用示例)

---

## 差异分析

### 功能概述

对比两个版本的配表，识别：
- 新增/删除的表
- 新增/删除的字段
- 数据变更的行
- 约束规则变更

### 差异类型

| 类型 | 说明 | 检测方法 |
|------|------|----------|
| 表级变更 | 新增/删除表 | 文件列表对比 |
| 结构变更 | 新增/删除/修改字段 | 表头对比 |
| 数据变更 | 行数据变化 | 逐行对比 |
| 约束变更 | 约束规则变化 | 约束提取对比 |

### 差异分析输出

```json
{
  "version_a": "v1.0.0",
  "version_b": "v1.1.0",
  "summary": {
    "tables_added": 1,
    "tables_removed": 0,
    "tables_modified": 3,
    "fields_added": 5,
    "fields_removed": 2,
    "rows_changed": 127
  },
  "changes": [
    {
      "table": "Hero.xlsx",
      "type": "field_added",
      "detail": {
        "field": "NewProperty",
        "type": "int",
        "position": 15
      }
    },
    {
      "table": "Hero.xlsx",
      "type": "data_changed",
      "detail": {
        "row_id": 1001,
        "field": "Attack",
        "old_value": 100,
        "new_value": 110
      }
    }
  ]
}
```

### 实现示例

```python
class DiffAnalyzer:
    """差异分析器"""

    def compare_versions(self, dir_a: str, dir_b: str) -> Dict:
        """对比两个版本"""
        analysis_a = self._analyze_version(dir_a)
        analysis_b = self._analyze_version(dir_b)

        return {
            "tables": self._compare_tables(analysis_a, analysis_b),
            "structures": self._compare_structures(analysis_a, analysis_b),
            "data": self._compare_data(analysis_a, analysis_b),
            "constraints": self._compare_constraints(analysis_a, analysis_b)
        }

    def _compare_tables(self, a: Dict, b: Dict) -> Dict:
        """对比表列表"""
        tables_a = {f["filename"] for f in a["files"]}
        tables_b = {f["filename"] for f in b["files"]}

        return {
            "added": list(tables_b - tables_a),
            "removed": list(tables_a - tables_b),
            "common": list(tables_a & tables_b)
        }
```

---

## 影响分析

### 功能概述

评估配表修改的影响范围：
- **直接影响** - 直接引用被修改表的表
- **间接影响** - 通过引用链传递影响的表
- **风险等级** - 根据影响范围和重要性评估

### 影响范围计算

```python
class ImpactAnalyzer:
    """影响分析器"""

    def analyze_impact(self, changes: List[Dict], relations: List[Dict]) -> Dict:
        """分析变更影响"""
        impact_graph = self._build_impact_graph(changes, relations)

        return {
            "direct_impact": self._get_direct_impact(impact_graph),
            "indirect_impact": self._get_indirect_impact(impact_graph),
            "risk_level": self._calculate_risk(impact_graph),
            "impact_paths": self._trace_impact_paths(impact_graph)
        }

    def _build_impact_graph(self, changes: List[Dict], relations: List[Dict]) -> Dict:
        """构建影响图"""
        # 获取被修改的表
        modified_tables = {c["table"] for c in changes}

        # 找出引用这些表的表
        impact_map = defaultdict(set)
        for rel in relations:
            if rel["target_table"] in modified_tables:
                impact_map[rel["target_table"]].add(rel["source_table"])

        return dict(impact_map)
```

### 风险等级评估

| 等级 | 条件 | 说明 |
|------|------|------|
| 高 | 修改中心表，影响 > 5 个表 | 核心数据变更 |
| 中 | 修改边缘表，影响 2-5 个表 | 局部影响 |
| 低 | 修改孤立表或影响 < 2 个表 | 影响有限 |

### 影响分析输出

```json
{
  "changes": ["Hero.xlsx"],
  "direct_impact": [
    {
      "table": "Card.xlsx",
      "reason": "引用 Hero.Id"
    },
    {
      "table": "ArenaScoreRewards.xlsx",
      "reason": "引用 Hero.Id"
    }
  ],
  "indirect_impact": [
    {
      "table": "Buff.xlsx",
      "path": "Card.xlsx → Hero.xlsx → Buff.xlsx",
      "distance": 2
    }
  ],
  "risk_level": "high",
  "recommendations": [
    "Hero.xlsx 是中心表，建议进行全面测试",
    "检查 Card.xlsx 和 ArenaScoreRewards.xlsx 的兼容性"
  ]
}
```

---

## 依赖追溯

### 功能概述

追踪多层级的依赖链路：
- 正向追溯 - 从当前表追溯被引用的表
- 反向追溯 - 从当前表追溯引用它的表
- 环路检测 - 检测循环引用

### 追溯方法

```python
class DependencyTracer:
    """依赖追溯器"""

    def trace_forward(self, table: str, relations: List[Dict], max_depth: int = 5) -> List[Dict]:
        """正向追溯：从表追溯其引用的表"""
        visited = set()
        result = []

        def dfs(current_table: str, depth: int, path: List[str]):
            if depth > max_depth or current_table in visited:
                return

            visited.add(current_table)

            # 找到当前表引用的所有表
            refs = [r for r in relations if r["source_table"] == current_table]
            for ref in refs:
                result.append({
                    "from": current_table,
                    "to": ref["target_table"],
                    "field": ref["source_field"],
                    "depth": depth,
                    "path": path + [ref["target_table"]]
                })
                dfs(ref["target_table"], depth + 1, path + [ref["target_table"]])

        dfs(table, 0, [table])
        return result

    def trace_backward(self, table: str, relations: List[Dict], max_depth: int = 5) -> List[Dict]:
        """反向追溯：从表追溯引用它的表"""
        # 实现与正向追溯类似，但关系方向相反
        ...
```

### 依赖追溯输出

```
依赖追溯: Hero.xlsx

【正向追溯】引用的表
├── Skill.xlsx (通过 Skills 字段)
│   └── EDamageType.xlsx (通过 DamageType 字段)
├── Buff.xlsx (通过 BuffIds 字段)
└── ECountry.xlsx (通过 Country 字段)

【反向追溯】被引用的表
├── Card.xlsx (引用 HeroId)
├── ArenaScoreRewards.xlsx (引用 Reward)
│   └── ArenaSeason.xlsx (引用 SeasonId)
└── SeasonPass.xlsx (通过 OpenDate 约束)

【环路检测】
未发现循环引用
```

---

## 使用示例

### 完整分析流程

```python
# 1. 差异分析
diff_analyzer = DiffAnalyzer()
diff_result = diff_analyzer.compare_versions(
    dir_a="/path/to/v1.0",
    dir_b="/path/to/v1.1"
)

print(f"变更汇总:")
print(f"  新增表: {len(diff_result['tables']['added'])}")
print(f"  删除表: {len(diff_result['tables']['removed'])}")
print(f"  修改表: {len(diff_result['tables']['common'])}")

# 2. 影响分析
impact_analyzer = ImpactAnalyzer()
impact_result = impact_analyzer.analyze_impact(
    changes=diff_result['changes'],
    relations=relations
)

print(f"\n影响分析:")
print(f"  风险等级: {impact_result['risk_level']}")
print(f"  直接影响: {len(impact_result['direct_impact'])} 个表")
print(f"  间接影响: {len(impact_result['indirect_impact'])} 个表")

# 3. 依赖追溯
tracer = DependencyTracer()
for table in diff_result['tables']['common']:
    dependencies = tracer.trace_forward(table, relations)
    print(f"\n{table} 依赖链:")
    for dep in dependencies:
        print(f"  {'  ' * dep['depth']}→ {dep['to']}")
```

### 输出示例

```
=== 配表差异分析报告 ===

版本: v1.0.0 → v1.1.0

【变更汇总】
- 新增表: 1 个 (NewFeature.xlsx)
- 删除表: 0 个
- 修改表: 3 个 (Hero.xlsx, Skill.xlsx, Card.xlsx)
- 新增字段: 5 个
- 删除字段: 2 个
- 数据变更: 127 行

【高影响变更】
⚠️ Hero.xlsx (风险等级: 高)
  - 新增字段: NewProperty
  - 数据变更: 89 行
  - 影响: Card.xlsx, ArenaScoreRewards.xlsx

【建议】
1. Hero.xlsx 是中心表，建议进行完整回归测试
2. 检查 Card.xlsx 和 ArenaScoreRewards.xlsx 的兼容性
3. 验证 NewProperty 字段的约束规则
```
