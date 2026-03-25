#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配表影响分析脚本

评估配表修改的影响范围和风险等级
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict


class ImpactAnalyzer:
    """影响分析器"""

    def __init__(self, relations: List[Dict] = None):
        self.relations = relations or []
        self._build_graph()

    def _build_graph(self):
        """构建关系图"""
        self.forward_refs = defaultdict(set)  # table -> set of tables it references
        self.backward_refs = defaultdict(set)  # table -> set of tables that reference it

        for rel in self.relations:
            source = rel["source_table"]
            target = rel["target_table"]
            self.forward_refs[source].add(target)
            self.backward_refs[target].add(source)

    def analyze_impact(self, changes: List[Dict]) -> Dict[str, Any]:
        """分析变更影响"""
        # 获取被修改的表
        modified_tables = self._extract_modified_tables(changes)

        # 分析影响
        impact = {
            "timestamp": datetime.now().isoformat(),
            "modified_tables": list(modified_tables),
            "direct_impact": self._get_direct_impact(modified_tables),
            "indirect_impact": self._get_indirect_impact(modified_tables),
            "risk_level": None,
            "recommendations": []
        }

        # 计算风险等级
        impact["risk_level"] = self._calculate_risk(impact)

        # 生成建议
        impact["recommendations"] = self._generate_recommendations(impact)

        return impact

    def _extract_modified_tables(self, changes: List[Dict]) -> Set[str]:
        """提取被修改的表"""
        tables = set()
        for change in changes:
            if "table" in change:
                tables.add(change["table"])
        return tables

    def _get_direct_impact(self, modified_tables: Set[str]) -> List[Dict]:
        """获取直接影响"""
        direct = []

        for table in modified_tables:
            # 找出引用此表的其他表
            referrers = self.backward_refs.get(table, set())
            for ref in referrers:
                direct.append({
                    "affected_table": ref,
                    "reason": f"引用 {table} 表",
                    "impact_type": "backward_reference"
                })

            # 找出此表引用的其他表
            references = self.forward_refs.get(table, set())
            for ref in references:
                direct.append({
                    "affected_table": ref,
                    "reason": f"被 {table} 表引用",
                    "impact_type": "forward_reference"
                })

        return direct

    def _get_indirect_impact(self, modified_tables: Set[str]) -> List[Dict]:
        """获取间接影响"""
        indirect = []
        visited = set()

        for table in modified_tables:
            # 追溯引用链
            paths = self._trace_impact_paths(table, max_depth=5, visited=visited)
            indirect.extend(paths)

        return indirect

    def _trace_impact_paths(self, start_table: str, max_depth: int = 5,
                           visited: Set[str] = None, path: List[str] = None) -> List[Dict]:
        """追溯影响路径"""
        if visited is None:
            visited = set()
        if path is None:
            path = [start_table]

        if start_table in visited or len(path) > max_depth:
            return []

        visited.add(start_table)
        results = []

        # 向前追溯（被引用）
        for ref in self.backward_refs.get(start_table, set()):
            new_path = path + [ref]
            results.append({
                "affected_table": ref,
                "path": " → ".join(new_path),
                "distance": len(new_path) - 1,
                "direction": "backward"
            })
            results.extend(self._trace_impact_paths(ref, max_depth, visited.copy(), new_path))

        # 向后追溯（引用）
        for ref in self.forward_refs.get(start_table, set()):
            new_path = path + [ref]
            results.append({
                "affected_table": ref,
                "path": " → ".join(new_path),
                "distance": len(new_path) - 1,
                "direction": "forward"
            })
            results.extend(self._trace_impact_paths(ref, max_depth, visited.copy(), new_path))

        return results

    def _calculate_risk(self, impact: Dict) -> str:
        """计算风险等级"""
        modified_tables = set(impact["modified_tables"])
        direct_count = len(impact["direct_impact"])
        indirect_count = len(impact["indirect_impact"])

        # 检查是否修改中心表
        center_tables = self._identify_center_tables()
        modifies_center = bool(modified_tables & center_tables)

        # 风险评估
        if modifies_center and direct_count > 5:
            return "high"
        elif modifies_center or direct_count > 3:
            return "medium"
        elif direct_count > 0:
            return "low"
        else:
            return "none"

    def _identify_center_tables(self) -> Set[str]:
        """识别中心表（被多次引用的表）"""
        ref_counts = defaultdict(int)
        for ref in self.backward_refs.values():
            for table in ref:
                ref_counts[table] += 1

        # 被引用 3 次以上为中心表
        return {table for table, count in ref_counts.items() if count >= 3}

    def _generate_recommendations(self, impact: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        risk = impact["risk_level"]
        modified_tables = impact["modified_tables"]

        if risk == "high":
            recommendations.append("⚠️ 高风险变更：涉及中心表，建议进行全面回归测试")
            center_tables = self._identify_center_tables()
            affected_center = modified_tables & center_tables
            if affected_center:
                recommendations.append(f"核心表 {', '.join(affected_center)} 被修改，请重点验证")

        if risk == "medium":
            recommendations.append("⚡ 中等风险：建议测试相关联的表")
            direct = [d["affected_table"] for d in impact["direct_impact"]]
            recommendations.append(f"受影响表: {', '.join(set(direct))}")

        if impact["direct_impact"]:
            recommendations.append(f"直接影响 {len(impact['direct_impact'])} 个表")

        if impact["indirect_impact"]:
            recommendations.append(f"间接影响 {len(impact['indirect_impact'])} 个表")

        return recommendations

    def load_relations_from_file(self, relations_file: str):
        """从文件加载关系"""
        with open(relations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.relations = data.get("relations", [])
        self._build_graph()

    def generate_report(self, impact: Dict) -> str:
        """生成影响分析报告"""
        lines = [
            "# 配表影响分析报告",
            f"",
            f"**生成时间**: {impact['timestamp']}",
            f"",
            f"## 变更表",
            f"",
            f"- 修改的表: {', '.join(impact['modified_tables'])}",
            f"",
            f"## 风险评估",
            f"",
            f"**风险等级**: {self._format_risk_level(impact['risk_level'])}",
            f""
        ]

        # 直接影响
        if impact["direct_impact"]:
            lines.extend([
                f"## 直接影响",
                f"",
                f"| 受影响表 | 原因 | 类型 |",
                f"|----------|------|------|"
            ])
            for imp in impact["direct_impact"]:
                impact_type = "反向引用" if imp["impact_type"] == "backward_reference" else "正向引用"
                lines.append(f"| {imp['affected_table']} | {imp['reason']} | {impact_type} |")
            lines.append("")

        # 间接影响
        if impact["indirect_impact"]:
            lines.extend([
                f"## 间接影响",
                f"",
                f"| 受影响表 | 距离 | 路径 |",
                f"|----------|------|------|"
            ])
            # 显示前 20 个
            for imp in impact["indirect_impact"][:20]:
                direction = "⬅️" if imp["direction"] == "backward" else "➡️"
                lines.append(f"| {imp['affected_table']} | {imp['distance']} | {direction} {imp['path']} |")

            if len(impact["indirect_impact"]) > 20:
                lines.append(f"| ... | ... | 还有 {len(impact['indirect_impact']) - 20} 个影响 |")
            lines.append("")

        # 建议
        if impact["recommendations"]:
            lines.extend([
                f"## 建议",
                f""
            ])
            for rec in impact["recommendations"]:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)

    def _format_risk_level(self, level: str) -> str:
        """格式化风险等级"""
        formats = {
            "high": "🔴 **高**",
            "medium": "🟡 **中**",
            "low": "🟢 **低**",
            "none": "⚪ **无**"
        }
        return formats.get(level, level)


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python impact_analyzer.py <关系文件.json> <变更文件.json> [输出文件]")
        print("或: python impact_analyzer.py --auto-scan <配表目录> <变更表列表>")
        sys.exit(1)

    analyzer = ImpactAnalyzer()

    # 加载关系
    if sys.argv[1] != "--auto-scan":
        relations_file = sys.argv[1]
        changes_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "impact_result.json"

        analyzer.load_relations_from_file(relations_file)

        # 加载变更
        with open(changes_file, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        if isinstance(changes, dict) and "changes" in changes:
            changes = changes["changes"]
    else:
        # 自动扫描模式（需要先有分析结果）
        print("自动扫描模式需要先运行 analyzer.py 生成关系文件")
        sys.exit(1)

    # 执行影响分析
    print("分析影响范围...")
    impact = analyzer.analyze_impact(changes)

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(impact, f, ensure_ascii=False, indent=2)

    print(f"JSON 结果已保存到: {output_file}")

    # 生成报告
    report = analyzer.generate_report(impact)
    report_file = output_file.replace('.json', '_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Markdown 报告已保存到: {report_file}")

    # 打印摘要
    print()
    print("影响分析摘要:")
    print(f"  修改表: {', '.join(impact['modified_tables'])}")
    print(f"  风险等级: {analyzer._format_risk_level(impact['risk_level'])}")
    print(f"  直接影响: {len(impact['direct_impact'])} 个表")
    print(f"  间接影响: {len(impact['indirect_impact'])} 个表")


if __name__ == "__main__":
    main()
