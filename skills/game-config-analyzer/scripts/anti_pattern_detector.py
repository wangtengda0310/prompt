#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反模式检测脚本

检测配表中的反模式
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict, deque


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

        def dfs(node: str, path: Set[str], path_list: List[str]):
            if node in path:
                # 找到环
                cycle_start = path_list.index(node)
                cycle = path_list[cycle_start:] + [node]
                detected.append({
                    "type": "circular_reference",
                    "severity": "high",
                    "cycle": cycle,
                    "message": f"检测到循环引用: {' → '.join(cycle)}",
                    "length": len(cycle)
                })
                return

            if node in visited_global:
                return

            visited_global.add(node)
            path.add(node)
            path_list.append(node)

            for neighbor in graph[node]:
                dfs(neighbor, path.copy(), path_list.copy())

        for start_node in list(graph.keys()):
            dfs(start_node, set(), [])

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
            for table in isolated if table
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
                "threshold": threshold,
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
            queue = deque([start_node])

            while queue:
                node = queue.popleft()
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
                "threshold": threshold,
                "message": f"{table} 的引用链路深度为 {depth}，超过推荐值 {threshold}"
            }
            for table, depth in deep_nested
        ]

    def _detect_anemic_models(self) -> List[Dict]:
        """检测贫血模型（只有 ID 引用，没有业务字段）"""
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
                    elif field_name not in ["Id", "CreateTime", "UpdateTime"]:
                        other_fields += 1

                # 如果 ID 引用占比超过 80%
                if id_refs > 3 and other_fields < id_refs * 0.2:
                    anemic.append({
                        "type": "anemic_model",
                        "severity": "low",
                        "table": table_name,
                        "id_references": id_refs,
                        "other_fields": other_fields,
                        "message": f"{table_name} 可能是贫血模型，ID 引用过多，业务字段较少"
                    })

        return anemic

    def load_data(self, analysis_file: str):
        """从分析结果文件加载数据"""
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.scan_result = data.get("scan_result", {})
            self.relations = data.get("relations", [])

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
                    lines.append(f"**长度**: {pattern['length']}")
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
                    lines.append(f"**依赖数**: {pattern['dependency_count']} (阈值: {pattern.get('threshold', 10)})")
                if "depth" in pattern:
                    lines.append(f"**深度**: {pattern['depth']} (阈值: {pattern.get('threshold', 5)})")
                lines.append("")

        if by_severity["low"]:
            lines.extend([
                f"## 🟢 低严重度反模式",
                f""
            ])
            for pattern in by_severity["low"]:
                lines.append(f"### {pattern['type'].replace('_', ' ').title()}")
                lines.append(f"**描述**: {pattern['message']}")
                if "table" in pattern:
                    lines.append(f"**表**: {pattern['table']}")
                if "id_references" in pattern:
                    lines.append(f"**ID 引用数**: {pattern['id_references']}")
                    lines.append(f"**其他字段数**: {pattern['other_fields']}")
                lines.append("")

        if by_severity["info"]:
            lines.extend([
                f"## 🔵 信息性反模式",
                f""
            ])
            for pattern in by_severity["info"][:10]:  # 只显示前 10 个
                lines.append(f"### {pattern['type'].replace('_', ' ').title()}")
                lines.append(f"**描述**: {pattern['message']}")
                if "table" in pattern:
                    lines.append(f"**表**: {pattern['table']}")
                lines.append("")

            if len(by_severity["info"]) > 10:
                lines.append(f"\n... 还有 {len(by_severity['info']) - 10} 个信息性反模式\n")

        return "\n".join(lines)

    def save_results(self, output_file: str = "anti_patterns.json"):
        """保存检测结果"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_count": len(self.anti_patterns),
            "by_severity": {
                "high": len([p for p in self.anti_patterns if p.get("severity") == "high"]),
                "medium": len([p for p in self.anti_patterns if p.get("severity") == "medium"]),
                "low": len([p for p in self.anti_patterns if p.get("severity") == "low"]),
                "info": len([p for p in self.anti_patterns if p.get("severity") == "info"])
            },
            "anti_patterns": self.anti_patterns
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"检测结果已保存到: {output_file}")


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python anti_pattern_detector.py <分析结果.json> [输出文件]")
        print("")
        print("检测的反模式类型:")
        print("  - 循环引用")
        print("  - 孤立表")
        print("  - 过度依赖")
        print("  - 深度嵌套")
        print("  - 贫血模型")
        sys.exit(1)

    analysis_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "anti_patterns.json"

    # 创建检测器
    detector = AntiPatternDetector()
    detector.load_data(analysis_file)

    # 执行检测
    print("检测反模式...")
    anti_patterns = detector.detect()

    # 保存结果
    detector.save_results(output_file)

    # 生成报告
    report = detector.generate_report()
    report_file = output_file.replace('.json', '_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已保存到: {report_file}")

    # 打印摘要
    print()
    print(f"检测到 {len(anti_patterns)} 个反模式")
    by_severity = defaultdict(int)
    for pattern in anti_patterns:
        by_severity[pattern.get("severity", "info")] += 1

    for severity in ["high", "medium", "low", "info"]:
        count = by_severity[severity]
        if count > 0:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "🔵"}.get(severity, "")
            print(f"  {icon} {severity.upper()}: {count}")


if __name__ == "__main__":
    main()
