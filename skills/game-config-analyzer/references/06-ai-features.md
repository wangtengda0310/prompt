# AI 功能

本文档详细说明配表分析的 AI 辅助功能。

## 目录

- [智能推荐](#智能推荐)
- [自然语言查询](#自然语言查询)
- [反模式检测](#反模式检测)
- [使用示例](#使用示例)

---

## 智能推荐

### 功能概述

基于分析结果提供智能建议：
- **优化建议** - 配表结构优化
- **一致性建议** - 跨表一致性改进
- **约束建议** - 缺失的约束规则
- **命名建议** - 字段命名规范

### 推荐类型

| 类型 | 说明 | 触发条件 |
|------|------|----------|
| 结构优化 | 建议表结构改进 | 检测反模式 |
| 约束补充 | 建议添加约束 | 发现隐含关系 |
| 命名规范 | 建议重命名 | 命名不一致 |
| 性能优化 | 建议性能改进 | 大表或复杂引用 |

### 实现示例

```python
class SmartRecommender:
    """智能推荐引擎"""

    def analyze_and_recommend(self, scan_result: Dict, relations: List[Dict]) -> List[Dict]:
        """分析并生成推荐"""
        recommendations = []

        # 1. 结构优化推荐
        recommendations.extend(self._recommend_structure_optimizations(scan_result))

        # 2. 约束补充推荐
        recommendations.extend(self._recommend_missing_constraints(scan_result, relations))

        # 3. 命名规范推荐
        recommendations.extend(self._recommend_naming_conventions(scan_result))

        # 4. 性能优化推荐
        recommendations.extend(self._recommend_performance_optimizations(scan_result, relations))

        return recommendations

    def _recommend_structure_optimizations(self, scan_result: Dict) -> List[Dict]:
        """推荐结构优化"""
        recommendations = []

        # 检测大表
        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                if sheet_info["row_count"] > 1000:
                    recommendations.append({
                        "type": "structure",
                        "priority": "medium",
                        "category": "large_table",
                        "message": f"{sheet_info['name']} 表数据量较大 ({sheet_info['row_count']} 行)",
                        "suggestion": "考虑分表或增加索引",
                        "table": sheet_info["name"]
                    })

        # 检测字段过多的表
        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                if len(sheet_info["headers"]) > 50:
                    recommendations.append({
                        "type": "structure",
                        "priority": "low",
                        "category": "many_fields",
                        "message": f"{sheet_info['name']} 表字段较多 ({len(sheet_info['headers'])} 个)",
                        "suggestion": "考虑垂直分表",
                        "table": sheet_info["name"]
                    })

        return recommendations

    def _recommend_missing_constraints(self, scan_result: Dict, relations: List[Dict]) -> List[Dict]:
        """推荐缺失的约束"""
        recommendations = []

        # 检测时间字段但没有顺序约束
        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                headers = sheet_info["headers"]
                field_names = [h["name"] for h in headers]

                has_start = "StartTime" in field_names
                has_end = "EndTime" in field_names

                if has_start and has_end:
                    # 检查是否已有约束
                    # 这里简化处理，实际应该检查现有约束
                    recommendations.append({
                        "type": "constraint",
                        "priority": "high",
                        "category": "time_order",
                        "message": f"{sheet_info['name']} 有 StartTime 和 EndTime 字段",
                        "suggestion": "确保添加 StartTime < EndTime 约束",
                        "table": sheet_info["name"]
                    })

        # 检测外键引用但没有约束
        for rel in relations:
            recommendations.append({
                "type": "constraint",
                "priority": "high",
                "category": "referential_integrity",
                "message": f"{rel['source_table']}.{rel['source_field']} 引用 {rel['target_table']}.{rel['target_field']}",
                "suggestion": "添加外键完整性验证",
                "table": rel["source_table"],
                "field": rel["source_field"]
            })

        return recommendations

    def _recommend_naming_conventions(self, scan_result: Dict) -> List[Dict]:
        """推荐命名规范"""
        recommendations = []

        # 分析字段命名模式
        field_patterns = defaultdict(list)

        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                for header in sheet_info["headers"]:
                    name = header["name"]
                    # 检测命名模式
                    if "Id" in name and not name.endswith("Id"):
                        field_patterns["id_position"].append((sheet_info["name"], name))

                    if "_" in name:
                        field_patterns["underscore"].append((sheet_info["name"], name))

        # 生成推荐
        if field_patterns["id_position"]:
            recommendations.append({
                "type": "naming",
                "priority": "low",
                "category": "id_suffix",
                "message": "检测到 ID 字段不在末尾的命名",
                "examples": field_patterns["id_position"][:5],
                "suggestion": "将 Id 后缀统一放在字段名末尾"
            })

        if field_patterns["underscore"]:
            recommendations.append({
                "type": "naming",
                "priority": "low",
                "category": "naming_style",
                "message": "检测到使用下划线的字段名",
                "examples": field_patterns["underscore"][:5],
                "suggestion": "考虑使用驼峰命名或统一风格"
            })

        return recommendations
```

---

## 自然语言查询

### 功能概述

使用自然语言查询配表：
- **语义解析** - 理解查询意图
- **查询转换** - 转换为结构化查询
- **结果展示** - 格式化展示结果

### 支持的查询模式

| 模式 | 示例 | 转换后 |
|------|------|--------|
| 引用查询 | "哪些表引用了 Hero 表" | `查找 target_table=Hero 的关系` |
| 字段查询 | "Hero 表有哪些时间字段" | `查找 Hero 表中含 time/date 的字段` |
| 约束查询 | "有哪些 OpenDate 约束" | `查找涉及 OpenDate 的约束` |
| 统计查询 | "哪个表被引用最多" | `统计 target_table 分组计数` |

### 实现示例

```python
class NaturalLanguageQuerier:
    """自然语言查询器"""

    def __init__(self, scan_result: Dict, relations: List[Dict], constraints: List[Dict]):
        self.scan_result = scan_result
        self.relations = relations
        self.constraints = constraints
        self.index = self._build_query_index()

    def _build_query_index(self) -> Dict:
        """构建查询索引"""
        return {
            "tables": {f["filename"]: f for f in self.scan_result["files"]},
            "relations_by_source": defaultdict(list),
            "relations_by_target": defaultdict(list),
            "constraints_by_table": defaultdict(list),
            "constraints_by_field": defaultdict(list)
        }

    def query(self, natural_query: str) -> Dict:
        """执行自然语言查询"""
        # 解析查询意图
        intent = self._parse_intent(natural_query)

        # 执行查询
        if intent["type"] == "reference_query":
            return self._execute_reference_query(intent)
        elif intent["type"] == "field_query":
            return self._execute_field_query(intent)
        elif intent["type"] == "constraint_query":
            return self._execute_constraint_query(intent)
        elif intent["type"] == "statistics_query":
            return self._execute_statistics_query(intent)
        else:
            return {"error": "无法理解查询意图"}

    def _parse_intent(self, query: str) -> Dict:
        """解析查询意图"""
        query_lower = query.lower()

        # 引用查询
        if "引用" in query_lower:
            if "哪些表" in query_lower or "谁" in query_lower:
                # "哪些表引用了 Hero" -> 查找引用 Hero 的表
                table_match = re.search(r'(\w+)\s*表', query)
                if table_match:
                    return {
                        "type": "reference_query",
                        "direction": "who_references",
                        "target": table_match.group(1)
                    }
            elif "引用了" in query_lower or "引用着" in query_lower:
                # "Hero 表引用了哪些表" -> 查找 Hero 引用的表
                table_match = re.search(r'(\w+)\s*表', query)
                if table_match:
                    return {
                        "type": "reference_query",
                        "direction": "references_what",
                        "source": table_match.group(1)
                    }

        # 字段查询
        if "字段" in query_lower or "列" in query_lower:
            table_match = re.search(r'(\w+)\s*表', query)
            field_type = None
            if "时间" in query_lower:
                field_type = "time"
            elif "id" in query_lower:
                field_type = "id"

            if table_match:
                return {
                    "type": "field_query",
                    "table": table_match.group(1),
                    "field_type": field_type
                }

        # 约束查询
        if "约束" in query_lower:
            field_match = re.search(r'(\w+)\s*约束', query)
            if field_match:
                return {
                    "type": "constraint_query",
                    "field": field_match.group(1)
                }

        # 统计查询
        if "最多" in query_lower or "最少" in query_lower or "多少" in query_lower:
            return {
                "type": "statistics_query",
                "metric": "reference_count"
            }

        return {"type": "unknown"}

    def _execute_reference_query(self, intent: Dict) -> Dict:
        """执行引用查询"""
        if intent["direction"] == "who_references":
            # 查找引用目标表的表
            target = intent["target"]
            refs = [r for r in self.relations if r["target_table"] == target]
            sources = list(set(r["source_table"] for r in refs))

            return {
                "query": f"哪些表引用了 {target} 表",
                "result": sources,
                "count": len(sources),
                "details": refs
            }

        elif intent["direction"] == "references_what":
            # 查找源表引用的表
            source = intent["source"]
            refs = [r for r in self.relations if r["source_table"] == source]
            targets = list(set(r["target_table"] for r in refs))

            return {
                "query": f"{source} 表引用了哪些表",
                "result": targets,
                "count": len(targets),
                "details": refs
            }

    def _execute_field_query(self, intent: Dict) -> Dict:
        """执行字段查询"""
        table = intent["table"]
        field_type = intent.get("field_type")

        # 查找表
        table_info = None
        for file_info in self.scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                if sheet_info["name"].lower() == table.lower():
                    table_info = sheet_info
                    break

        if not table_info:
            return {"error": f"未找到表 {table}"}

        # 筛选字段
        fields = table_info["headers"]
        if field_type == "time":
            fields = [f for f in fields if any(kw in f["name"].lower() for kw in ["time", "date", "start", "end"])]
        elif field_type == "id":
            fields = [f for f in fields if "id" in f["name"].lower()]

        return {
            "query": f"{table} 表的字段",
            "table": table,
            "fields": [{"name": f["name"], "type": f["type"], "chs_name": f["chs_name"]} for f in fields],
            "count": len(fields)
        }

    def _execute_constraint_query(self, intent: Dict) -> Dict:
        """执行约束查询"""
        field = intent["field"]

        constraints = [c for c in self.constraints if field in c.get("fields", [])]

        return {
            "query": f"{field} 相关的约束",
            "field": field,
            "constraints": constraints,
            "count": len(constraints)
        }

    def _execute_statistics_query(self, intent: Dict) -> Dict:
        """执行统计查询"""
        if intent["metric"] == "reference_count":
            # 统计每个表被引用的次数
            ref_counts = defaultdict(int)
            for rel in self.relations:
                ref_counts[rel["target_table"]] += 1

            sorted_counts = sorted(ref_counts.items(), key=lambda x: x[1], reverse=True)

            return {
                "query": "表被引用次数统计",
                "results": [{"table": t, "count": c} for t, c in sorted_counts],
                "most_referenced": sorted_counts[0] if sorted_counts else None
            }
```

---

## 反模式检测

### 功能概述

检测常见的配表反模式：
- **循环引用** - A 引用 B，B 引用 A
- **孤立表** - 既不引用别人也不被引用
- **过度依赖** - 单个表引用过多表
- **深度嵌套** - 引用链路过深

### 反模式类型

| 反模式 | 描述 | 风险 |
|--------|------|------|
| 循环引用 | 表之间存在循环依赖 | 数据一致性难以保证 |
| 孤立表 | 与其他表无任何关联 | 可能是冗余数据 |
| 过度依赖 | 一个表引用 >10 个表 | 维护困难 |
| 深度嵌套 | 引用链路 >5 层 | 性能和可维护性问题 |
| 贫血模型 | 只有 ID 引用无业务字段 | 设计不合理 |

### 实现示例

```python
class AntiPatternDetector:
    """反模式检测器"""

    def detect(self, relations: List[Dict], scan_result: Dict) -> List[Dict]:
        """检测所有反模式"""
        anti_patterns = []

        # 1. 循环引用检测
        anti_patterns.extend(self._detect_circular_references(relations))

        # 2. 孤立表检测
        anti_patterns.extend(self._detect_isolated_tables(relations, scan_result))

        # 3. 过度依赖检测
        anti_patterns.extend(self._detect_over_dependency(relations))

        # 4. 深度嵌套检测
        anti_patterns.extend(self._detect_deep_nesting(relations))

        return anti_patterns

    def _detect_circular_references(self, relations: List[Dict]) -> List[Dict]:
        """检测循环引用"""
        # 构建邻接表
        graph = defaultdict(list)
        for rel in relations:
            graph[rel["source_table"]].append(rel["target_table"])

        # DFS 检测环
        detected = []

        def dfs(node: str, path: Set[str], visited: Set[str]):
            if node in path:
                # 找到环
                cycle_start = list(path).index(node)
                cycle = list(path)[cycle_start:] + [node]
                detected.append({
                    "type": "circular_reference",
                    "severity": "high",
                    "cycle": cycle,
                    "message": f"检测到循环引用: {' → '.join(cycle)}"
                })
                return

            if node in visited:
                return

            visited.add(node)
            path.add(node)

            for neighbor in graph[node]:
                dfs(neighbor, path.copy(), visited.copy())

        for start_node in graph:
            dfs(start_node, set(), set())

        return detected

    def _detect_isolated_tables(self, relations: List[Dict], scan_result: Dict) -> List[Dict]:
        """检测孤立表"""
        # 获取所有表
        all_tables = set()
        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                all_tables.add(sheet_info["name"])

        # 获取有关系的表
        related_tables = set()
        for rel in relations:
            related_tables.add(rel["source_table"])
            related_tables.add(rel["target_table"])

        # 找出孤立表
        isolated = all_tables - related_tables

        return [
            {
                "type": "isolated_table",
                "severity": "info",
                "table": table,
                "message": f"{table} 表与其他表无关联关系"
            }
            for table in isolated
        ]

    def _detect_over_dependency(self, relations: List[Dict]) -> List[Dict]:
        """检测过度依赖"""
        # 统计每个表引用的表数量
        out_degree = defaultdict(int)
        for rel in relations:
            out_degree[rel["source_table"]] += 1

        # 找出超过阈值的表
        threshold = 10
        over_dependent = [(t, c) for t, c in out_degree.items() if c > threshold]

        return [
            {
                "type": "over_dependency",
                "severity": "medium",
                "table": table,
                "dependency_count": count,
                "message": f"{table} 表引用了 {count} 个表，超过推荐值 {threshold}"
            }
            for table, count in over_dependent
        ]

    def _detect_deep_nesting(self, relations: List[Dict]) -> List[Dict]:
        """检测深度嵌套"""
        # 构建邻接表
        graph = defaultdict(list)
        for rel in relations:
            graph[rel["source_table"]].append(rel["target_table"])

        # BFS 计算最大深度
        max_depths = {}
        threshold = 5

        for start_node in graph:
            visited = {start_node: 0}
            queue = [start_node]

            while queue:
                node = queue.pop(0)
                current_depth = visited[node]

                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited[neighbor] = current_depth + 1
                        queue.append(neighbor)

            max_depth = max(visited.values())
            max_depths[start_node] = max_depth

        # 找出深度过大的
        deep_nested = [(t, d) for t, d in max_depths.items() if d > threshold]

        return [
            {
                "type": "deep_nesting",
                "severity": "medium",
                "table": table,
                "depth": depth,
                "message": f"{table} 的引用链路深度为 {depth}，超过推荐值 {threshold}"
            }
            for table, depth in deep_nested
        ]
```

---

## 使用示例

### 智能推荐

#### 使用脚本

```bash
# 基于分析结果生成推荐
python scripts/smart_recommender.py analysis_result.json recommendations.json

# 输出：
# - recommendations.json (JSON 格式推荐)
# - recommendations_report.md (Markdown 报告)
# - recommendations_anti_patterns.json (反模式检测)
# - recommendations_anti_patterns_report.md (反模式报告)
```

#### Python API

```python
from scripts.smart_recommender import SmartRecommender

recommender = SmartRecommender(scan_result, relations)
recommendations = recommender.analyze_and_recommend()

# 按优先级分组
grouped = recommender.prioritize_recommendations()
print(f"高优先级: {len(grouped['high'])}")
print(f"中优先级: {len(grouped['medium'])}")

# 生成报告
report = recommender.generate_report()
```

### 反模式检测

#### 使用脚本

```bash
# 独立反模式检测
python scripts/anti_pattern_detector.py analysis_result.json anti_patterns.json

# 输出：
# - anti_patterns.json (检测结果)
# - anti_patterns_report.md (详细报告)
```

#### Python API

```python
from scripts.anti_pattern_detector import AntiPatternDetector

detector = AntiPatternDetector(relations, scan_result)
anti_patterns = detector.detect()

# 生成报告
report = detector.generate_report()
```

### 批量变更模拟

#### 使用脚本

```bash
# 单表变更模拟
python scripts/simulator.py relations.json change.json

# 批量变更模拟
cat <<EOF > batch_changes.json
[
  {
    "table": "Hero",
    "changes": [
      {"operation": "update", "field": "OpenDate", "row_id": 1001}
    ]
  },
  {
    "table": "Skill",
    "changes": [
      {"operation": "update", "field": "Damage", "row_id": 2001}
    ]
  }
]
EOF

python scripts/simulator.py relations.json batch_changes.json
```

### 配合使用

```bash
# 完整分析流程
python scripts/analyzer.py ./configs > analysis.json
python scripts/smart_recommender.py analysis.json
python scripts/anti_pattern_detector.py analysis.json
```

---

## 脚本完整列表

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `analyzer.py` | 核心分析 | 配表目录 | 分析结果 |
| `diff_analyzer.py` | 差异分析 | 两个目录 | 差异报告 |
| `impact_analyzer.py` | 影响分析 | 关系+变更 | 影响报告 |
| `validator.py` | 数据验证 | 配表目录 | 验证报告 |
| `search.py` | 全文搜索 | 目录+查询 | 搜索结果 |
| `batch_operator.py` | 批量操作 | 目录+操作 | 操作结果 |
| `simulator.py` | 配置模拟器 | 关系+变更 | 模拟报告 |
| `smart_recommender.py` | 智能推荐 | 分析结果 | 推荐报告 |
| `anti_pattern_detector.py` | 反模式检测 | 分析结果 | 反模式报告 |
