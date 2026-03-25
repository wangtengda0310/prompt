#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能推荐脚本

基于配表分析提供智能建议
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict


class SmartRecommender:
    """智能推荐引擎"""

    def __init__(self, scan_result: Dict = None, relations: List[Dict] = None):
        self.scan_result = scan_result or {}
        self.relations = relations or []
        self.recommendations = []

    def analyze_and_recommend(self) -> List[Dict[str, Any]]:
        """分析并生成推荐"""
        self.recommendations = []

        # 1. 结构优化推荐
        self.recommendations.extend(self._recommend_structure_optimizations())

        # 2. 约束补充推荐
        self.recommendations.extend(self._recommend_missing_constraints())

        # 3. 命名规范推荐
        self.recommendations.extend(self._recommend_naming_conventions())

        # 4. 性能优化推荐
        self.recommendations.extend(self._recommend_performance_optimizations())

        # 5. 数据质量推荐
        self.recommendations.extend(self._recommend_data_quality_improvements())

        return self.recommendations

    def _recommend_structure_optimizations(self) -> List[Dict]:
        """推荐结构优化"""
        recommendations = []

        if not self.scan_result:
            return recommendations

        # 检测大表
        for file_info in self.scan_result.get("files", []):
            for sheet_info in file_info.get("sheets", []):
                row_count = sheet_info.get("row_count", 0)
                table_name = sheet_info.get("name", "")

                if row_count > 1000:
                    recommendations.append({
                        "type": "structure",
                        "priority": "medium",
                        "category": "large_table",
                        "message": f"{table_name} 表数据量较大 ({row_count} 行)",
                        "suggestion": "考虑分表或增加索引",
                        "table": table_name,
                        "metric": row_count
                    })

                # 检测字段过多的表
                headers = sheet_info.get("headers", [])
                if len(headers) > 50:
                    recommendations.append({
                        "type": "structure",
                        "priority": "low",
                        "category": "many_fields",
                        "message": f"{table_name} 表字段较多 ({len(headers)} 个)",
                        "suggestion": "考虑垂直分表",
                        "table": table_name,
                        "metric": len(headers)
                    })

        return recommendations

    def _recommend_missing_constraints(self) -> List[Dict]:
        """推荐缺失的约束"""
        recommendations = []

        if not self.scan_result:
            return recommendations

        # 收集所有表和字段
        all_fields = defaultdict(set)
        for file_info in self.scan_result.get("files", []):
            for sheet_info in file_info.get("sheets", []):
                table_name = sheet_info.get("name", "")
                for header in sheet_info.get("headers", []):
                    field_name = header.get("name", "")
                    if field_name:
                        all_fields[table_name].add(field_name)

        # 检测时间字段但没有顺序约束
        for table_name, fields in all_fields.items():
            has_start = any("starttime" in f.lower() or "start" in f.lower() for f in fields)
            has_end = any("endtime" in f.lower() or "end" in f.lower() for f in fields)

            if has_start and has_end:
                recommendations.append({
                    "type": "constraint",
                    "priority": "high",
                    "category": "time_order",
                    "message": f"{table_name} 有 StartTime 和 EndTime 字段",
                    "suggestion": "确保添加 StartTime < EndTime 约束",
                    "table": table_name
                })

        # 检测外键引用
        for rel in self.relations:
            recommendations.append({
                "type": "constraint",
                "priority": "high",
                "category": "referential_integrity",
                "message": f"{rel['source_table']}.{rel['source_field']} 引用 {rel['target_table']}.{rel['target_field']}",
                "suggestion": "添加外键完整性验证",
                "table": rel["source_table"],
                "field": rel["source_field"]
            })

        # 去重
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            key = (rec["table"], rec["category"])
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)

        return unique_recommendations

    def _recommend_naming_conventions(self) -> List[Dict]:
        """推荐命名规范"""
        recommendations = []

        if not self.scan_result:
            return recommendations

        # 分析字段命名模式
        field_patterns = defaultdict(list)

        for file_info in self.scan_result.get("files", []):
            for sheet_info in file_info.get("sheets", []):
                table_name = sheet_info.get("name", "")
                for header in sheet_info.get("headers", []):
                    name = header.get("name", "")

                    # 检测命名模式
                    if "Id" in name and not name.endswith("Id"):
                        field_patterns["id_position"].append((table_name, name))

                    if "_" in name:
                        field_patterns["underscore"].append((table_name, name))

                    # 检测不一致的大小写
                    if re.match(r'^[a-z]+[A-Z]', name):
                        field_patterns["inconsistent_case"].append((table_name, name))

        # 生成推荐
        if field_patterns["id_position"]:
            examples = field_patterns["id_position"][:3]
            recommendations.append({
                "type": "naming",
                "priority": "low",
                "category": "id_suffix",
                "message": "检测到 ID 字段不在末尾的命名",
                "examples": [{"table": t, "field": f} for t, f in examples],
                "suggestion": "将 Id 后缀统一放在字段名末尾"
            })

        if field_patterns["underscore"]:
            count = len(field_patterns["underscore"])
            recommendations.append({
                "type": "naming",
                "priority": "low",
                "category": "naming_style",
                "message": f"检测到 {count} 个使用下划线的字段名",
                "suggestion": "考虑使用驼峰命名或统一风格"
            })

        return recommendations

    def _recommend_performance_optimizations(self) -> List[Dict]:
        """推荐性能优化"""
        recommendations = []

        if not self.relations:
            return recommendations

        # 统计每个表的引用情况
        ref_counts = defaultdict(int)
        out_refs = defaultdict(int)

        for rel in self.relations:
            source = rel["source_table"]
            target = rel["target_table"]
            ref_counts[target] += 1
            out_refs[source] += 1

        # 检测过度引用
        for table, count in out_refs.items():
            if count > 10:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "category": "too_many_references",
                    "message": f"{table} 引用了 {count} 个其他表",
                    "suggestion": "考虑引入中间表或重构关系",
                    "table": table,
                    "metric": count
                })

        # 检测热门表（被多次引用）
        for table, count in ref_counts.items():
            if count > 5:
                recommendations.append({
                    "type": "performance",
                    "priority": "low",
                    "category": "hot_table",
                    "message": f"{table} 被 {count} 个表引用",
                    "suggestion": "考虑添加缓存或索引",
                    "table": table,
                    "metric": count
                })

        return recommendations

    def _recommend_data_quality_improvements(self) -> List[Dict]:
        """推荐数据质量改进"""
        recommendations = []

        # 检测可能的冗余字段
        field_names = defaultdict(list)
        for file_info in self.scan_result.get("files", []):
            for sheet_info in file_info.get("sheets", []):
                table_name = sheet_info.get("name", "")
                for header in sheet_info.get("headers", []):
                    field_name = header.get("name", "")
                    if field_name:
                        field_names[field_name].append(table_name)

        # 找出在多个表中重复的字段
        for field_name, tables in field_names.items():
            if len(tables) > 5 and field_name not in ["Id", "Name", "Type"]:
                recommendations.append({
                    "type": "quality",
                    "priority": "low",
                    "category": "potential_redundancy",
                    "message": f"字段 {field_name} 出现在 {len(tables)} 个表中",
                    "suggestion": "检查是否可以通过表关系减少冗余",
                    "field": field_name,
                    "tables": tables[:5]
                })

        return recommendations

    def prioritize_recommendations(self) -> Dict[str, List[Dict]]:
        """按优先级分组推荐"""
        grouped = {
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }

        for rec in self.recommendations:
            priority = rec.get("priority", "info")
            grouped[priority].append(rec)

        return grouped

    def generate_report(self) -> str:
        """生成推荐报告"""
        grouped = self.prioritize_recommendations()

        lines = [
            "# 配表优化建议报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**建议总数**: {len(self.recommendations)}",
            f"",
            f"## 按优先级分类",
            f"",
            f"| 优先级 | 数量 |",
            f"|--------|------|"
        ]

        for priority, count in [("high", len(grouped["high"])),
                                ("medium", len(grouped["medium"])),
                                ("low", len(grouped["low"])),
                                ("info", len(grouped["info"]))]:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "🔵"}.get(priority, "")
            lines.append(f"| {icon} {priority.upper()} | {count} |")

        lines.append("")

        # 详细建议
        for priority in ["high", "medium", "low", "info"]:
            if grouped[priority]:
                lines.extend([
                    f"## {priority.upper()} 优先级建议",
                    f""
                ])

                for rec in grouped[priority]:
                    lines.append(f"### {rec['category'].replace('_', ' ').title()}")
                    lines.append(f"**类型**: {rec['type']}")
                    lines.append(f"**描述**: {rec['message']}")
                    lines.append(f"**建议**: {rec['suggestion']}")

                    if "table" in rec:
                        lines.append(f"**表**: {rec['table']}")
                    if "field" in rec:
                        lines.append(f"**字段**: {rec['field']}")
                    if "examples" in rec:
                        lines.append(f"**示例**:")
                        for ex in rec["examples"]:
                            lines.append(f"  - {ex['table']}.{ex['field']}")

                    lines.append("")

        return "\n".join(lines)

    def save_recommendations(self, output_file: str = "recommendations.json"):
        """保存推荐到文件"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_count": len(self.recommendations),
            "by_priority": self.prioritize_recommendations(),
            "recommendations": self.recommendations
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"推荐已保存到: {output_file}")


class AntiPatternDetector:
    """反模式检测器"""

    def __init__(self, relations: List[Dict] = None, scan_result: Dict = None):
        self.relations = relations or []
        self.scan_result = scan_result or {}
        self.anti_patterns = []

    def detect(self) -> List[Dict]:
        """检测所有反模式"""
        self.anti_patterns = []

        # 1. 循环引用检测
        self.anti_patterns.extend(self._detect_circular_references())

        # 2. 孤立表检测
        self.anti_patterns.extend(self._detect_isolated_tables())

        # 3. 过度依赖检测
        self.anti_patterns.extend(self._detect_over_dependency())

        # 4. 深度嵌套检测
        self.anti_patterns.extend(self._detect_deep_nesting())

        # 5. 贫血模型检测
        self.anti_patterns.extend(self._detect_anemic_models())

        return self.anti_patterns

    def _detect_circular_references(self) -> List[Dict]:
        """检测循环引用"""
        # 构建邻接表
        graph = defaultdict(list)
        for rel in self.relations:
            graph[rel["source_table"]].append(rel["target_table"])

        detected = []
        visited_global = set()

        def dfs(node: str, path: Set[str]):
            if node in path:
                # 找到环
                cycle_list = list(path)
                cycle_start = cycle_list.index(node)
                cycle = cycle_list[cycle_start:] + [node]
                detected.append({
                    "type": "circular_reference",
                    "severity": "high",
                    "cycle": cycle,
                    "message": f"检测到循环引用: {' → '.join(cycle)}"
                })
                return

            if node in visited_global:
                return

            visited_global.add(node)
            path.add(node)

            for neighbor in graph[node]:
                dfs(neighbor, path.copy())

        for start_node in graph:
            dfs(start_node, set())

        return detected

    def _detect_isolated_tables(self) -> List[Dict]:
        """检测孤立表"""
        # 获取所有表
        all_tables = set()
        for file_info in self.scan_result.get("files", []):
            for sheet_info in file_info.get("sheets", []):
                all_tables.add(sheet_info.get("name", ""))

        # 获取有关系的表
        related_tables = set()
        for rel in self.relations:
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

    def _detect_over_dependency(self) -> List[Dict]:
        """检测过度依赖"""
        # 统计每个表引用的表数量
        out_degree = defaultdict(int)
        for rel in self.relations:
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

    def _detect_deep_nesting(self) -> List[Dict]:
        """检测深度嵌套"""
        # 构建邻接表
        graph = defaultdict(list)
        for rel in self.relations:
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

    def _detect_anemic_models(self) -> List[Dict]:
        """检测贫血模型（只有 ID 引用，没有业务字段）"""
        # 这里简化处理
        anemic = []

        for file_info in self.scan_result.get("files", []):
            for sheet_info in file_info.get("sheets", []):
                table_name = sheet_info.get("name", "")
                headers = sheet_info.get("headers", [])

                # 统计 ID 引用字段和其他字段
                id_refs = 0
                other_fields = 0

                for header in headers:
                    field_name = header.get("name", "")
                    if field_name.endswith("Id") or field_name.endswith("Ids"):
                        id_refs += 1
                    else:
                        other_fields += 1

                # 如果 ID 引用占比超过 80%
                if id_refs > 3 and other_fields < id_refs * 0.2:
                    anemic.append({
                        "type": "anemic_model",
                        "severity": "info",
                        "table": table_name,
                        "id_references": id_refs,
                        "other_fields": other_fields,
                        "message": f"{table_name} 可能是贫血模型，ID 引用过多，业务字段较少"
                    })

        return anemic

    def generate_report(self) -> str:
        """生成反模式报告"""
        lines = [
            "# 配表反模式检测报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**检测到**: {len(self.anti_patterns)} 个反模式",
            f""
        ]

        # 按严重程度分组
        by_severity = defaultdict(list)
        for pattern in self.anti_patterns:
            severity = pattern.get("severity", "info")
            by_severity[severity].append(pattern)

        # 统计
        lines.extend([
            f"## 按严重程度统计",
            f"",
            f"| 严重程度 | 数量 |",
            f"|----------|------|"
        ])

        for severity in ["high", "medium", "low", "info"]:
            count = len(by_severity[severity])
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "🔵"}.get(severity, "")
            lines.append(f"| {icon} {severity.upper()} | {count} |")

        lines.append("")

        # 详细信息
        if by_severity["high"]:
            lines.extend([
                f"## 🔴 高严重度反模式",
                f""
            ])
            for pattern in by_severity["high"]:
                lines.append(f"### {pattern['type'].replace('_', ' ').title()}")
                lines.append(f"**描述**: {pattern['message']}")
                if "cycle" in pattern:
                    lines.append(f"**循环路径**: {' → '.join(pattern['cycle'])}")
                lines.append("")

        if by_severity["medium"]:
            lines.extend([
                f"## 🟡 中等严重度反模式",
                f""
            ])
            for pattern in by_severity["medium"]:
                lines.append(f"### {pattern['type'].replace('_', ' ').title()}")
                lines.append(f"**描述**: {pattern['message']}")
                if "table" in pattern:
                    lines.append(f"**表**: {pattern['table']}")
                if "dependency_count" in pattern:
                    lines.append(f"**依赖数**: {pattern['dependency_count']}")
                if "depth" in pattern:
                    lines.append(f"**深度**: {pattern['depth']}")
                lines.append("")

        if by_severity["info"]:
            lines.extend([
                f"## 🔵 信息性反模式",
                f""
            ])
            for pattern in by_severity["info"][:10]:  # 只显示前 10 个
                lines.append(f"### {pattern['type'].replace('_', ' ').title()}")
                lines.append(f"**描述**: {pattern['message']}")
                lines.append("")

        return "\n".join(lines)


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python smart_recommender.py <分析结果.json> [输出文件]")
        print("")
        print("功能:")
        print("  - 生成优化建议")
        print("  - 检测反模式")
        sys.exit(1)

    analysis_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "smart_recommendations.json"

    # 加载分析结果
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scan_result = data.get("scan_result", {})
    relations = data.get("relations", [])

    # 生成推荐
    print("生成优化建议...")
    recommender = SmartRecommender(scan_result, relations)
    recommendations = recommender.analyze_and_recommend()
    recommender.save_recommendations(output_file)

    # 检测反模式
    print("检测反模式...")
    detector = AntiPatternDetector(relations, scan_result)
    anti_patterns = detector.detect()

    # 保存反模式
    anti_pattern_file = output_file.replace('.json', '_anti_patterns.json')
    with open(anti_pattern_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_count": len(anti_patterns),
            "anti_patterns": anti_patterns
        }, f, ensure_ascii=False, indent=2)

    print(f"反模式已保存到: {anti_pattern_file}")

    # 生成报告
    rec_report = recommender.generate_report()
    rec_report_file = output_file.replace('.json', '_report.md')
    with open(rec_report_file, 'w', encoding='utf-8') as f:
        f.write(rec_report)

    print(f"推荐报告已保存到: {rec_report_file}")

    anti_report = detector.generate_report()
    anti_report_file = anti_pattern_file.replace('.json', '_report.md')
    with open(anti_report_file, 'w', encoding='utf-8') as f:
        f.write(anti_report)

    print(f"反模式报告已保存到: {anti_report_file}")

    # 打印摘要
    print()
    print(f"建议总数: {len(recommendations)}")
    grouped = recommender.prioritize_recommendations()
    print(f"  高优先级: {len(grouped['high'])}")
    print(f"  中优先级: {len(grouped['medium'])}")
    print(f"  低优先级: {len(grouped['low'])}")
    print(f"反模式数: {len(anti_patterns)}")


if __name__ == "__main__":
    main()
