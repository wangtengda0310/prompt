#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配表配置模拟器

What-if 分析，预览变更影响
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict, deque


class ConfigSimulator:
    """配置模拟器"""

    def __init__(self, relations: List[Dict] = None):
        self.relations = relations or []
        self._build_graph()

    def _build_graph(self):
        """构建关系图"""
        self.forward_refs = defaultdict(set)
        self.backward_refs = defaultdict(set)

        for rel in self.relations:
            source = rel["source_table"]
            target = rel["target_table"]
            self.forward_refs[source].add(target)
            self.backward_refs[target].add(source)

    def simulate_change(self, table: str, changes: List[Dict], relations: List[Dict] = None) -> Dict[str, Any]:
        """模拟配置变更"""
        if relations:
            self.relations = relations
            self._build_graph()

        simulation = {
            "simulation_id": f"sim-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "table": table,
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
        indirect = self._trace_indirect_impact(table, max_depth=5)
        simulation["indirect_impact"] = indirect

        # 3. 风险评估
        simulation["risks"] = self._assess_risks(simulation)

        # 4. 生成回滚方案
        simulation["rollback"] = self._generate_rollback(table, changes)

        return simulation

    def _analyze_direct_change(self, table: str, change: Dict) -> Dict[str, Any]:
        """分析直接变更"""
        operation = change.get("operation", "unknown")
        field = change.get("field", "")
        row_id = change.get("row_id")

        impact = {
            "operation": operation,
            "field": field,
            "row_id": row_id,
            "is_primary_key": (field == "Id"),
            "is_foreign_key": self._is_foreign_key(table, field),
            "affects_other_tables": self._affects_other_tables(table, field)
        }

        return impact

    def _is_foreign_key(self, table: str, field: str) -> bool:
        """检查是否是外键"""
        for rel in self.relations:
            if rel["source_table"] == table and rel["source_field"] == field:
                return True
        return False

    def _affects_other_tables(self, table: str, field: str) -> List[str]:
        """获取受影响的其他表"""
        affected = []

        # 检查是否有其他表引用此表的此字段
        for rel in self.relations:
            if rel["target_table"] == table and rel["target_field"] == field:
                affected.append(rel["source_table"])

        return affected

    def _trace_indirect_impact(self, start_table: str, max_depth: int = 5) -> List[Dict]:
        """追溯间接影响"""
        indirect = []
        visited = set()

        # 向前追溯（被引用）
        forward_queue = deque([(start_table, 0, [start_table])])
        while forward_queue:
            current, depth, path = forward_queue.popleft()

            if current in visited or depth > max_depth:
                continue

            visited.add(current)

            for ref in self.backward_refs.get(current, set()):
                if ref not in path:
                    new_path = path + [ref]
                    indirect.append({
                        "table": ref,
                        "path": " → ".join(new_path),
                        "distance": depth + 1,
                        "direction": "forward",
                        "relationship": "引用当前表"
                    })
                    forward_queue.append((ref, depth + 1, new_path))

        # 向后追溯（引用）
        visited = set()
        backward_queue = deque([(start_table, 0, [start_table])])
        while backward_queue:
            current, depth, path = backward_queue.popleft()

            if current in visited or depth > max_depth:
                continue

            visited.add(current)

            for ref in self.forward_refs.get(current, set()):
                if ref not in path:
                    new_path = path + [ref]
                    indirect.append({
                        "table": ref,
                        "path": " → ".join(new_path),
                        "distance": depth + 1,
                        "direction": "backward",
                        "relationship": "被当前表引用"
                    })
                    backward_queue.append((ref, depth + 1, new_path))

        return indirect

    def _assess_risks(self, simulation: Dict) -> List[Dict]:
        """评估风险"""
        risks = []

        # 检查主键修改
        for impact in simulation["direct_impact"]:
            if impact.get("is_primary_key"):
                risks.append({
                    "level": "high",
                    "type": "primary_key_change",
                    "message": f"修改主键 {impact['field']} 可能导致引用失效",
                    "suggestion": "确保所有引用此主键的表已更新",
                    "affected_tables": impact.get("affects_other_tables", [])
                })

        # 检查外键修改
        for impact in simulation["direct_impact"]:
            if impact.get("is_foreign_key"):
                risks.append({
                    "level": "high",
                    "type": "foreign_key_change",
                    "message": f"修改外键 {impact['field']} 可能影响关联关系",
                    "suggestion": "验证引用的数据存在",
                    "affected_tables": impact.get("affects_other_tables", [])
                })

        # 检查删除操作
        for impact in simulation["direct_impact"]:
            if impact.get("operation") == "delete":
                risks.append({
                    "level": "high",
                    "type": "data_deletion",
                    "message": f"删除数据可能影响引用表",
                    "suggestion": "检查并更新或删除引用关系"
                })

        # 检查间接影响数量
        indirect_count = len(simulation["indirect_impact"])
        if indirect_count > 10:
            risks.append({
                "level": "medium",
                "type": "wide_impact",
                "message": f"变更将间接影响 {indirect_count} 个表",
                "suggestion": "建议进行全面测试"
            })
        elif indirect_count > 5:
            risks.append({
                "level": "low",
                "type": "moderate_impact",
                "message": f"变更将间接影响 {indirect_count} 个表",
                "suggestion": "验证相关表的兼容性"
            })

        # 检查中心表
        if self._is_center_table(simulation["table"]):
            risks.append({
                "level": "high",
                "type": "center_table_modification",
                "message": f"{simulation['table']} 是中心表，修改影响较大",
                "suggestion": "优先进行全面回归测试"
            })

        return risks

    def _is_center_table(self, table: str) -> bool:
        """检查是否是中心表"""
        # 被引用 3 次以上为中心表
        ref_count = len(self.backward_refs.get(table, set()))
        return ref_count >= 3

    def _generate_rollback(self, table: str, changes: List[Dict]) -> Dict[str, Any]:
        """生成回滚方案"""
        rollback = {
            "steps": [],
            "sql": [],
            "scripts": []
        }

        for change in changes:
            operation = change.get("operation")
            field = change.get("field", "")
            row_id = change.get("row_id")
            old_value = change.get("old_value")
            new_value = change.get("new_value")

            if operation == "update":
                rollback["steps"].append({
                    "action": "update",
                    "table": table,
                    "field": field,
                    "row_id": row_id,
                    "restore_to": old_value
                })
                rollback["sql"].append(
                    f"UPDATE {table} SET {field} = '{old_value}' WHERE Id = {row_id}"
                )

            elif operation == "delete":
                rollback["steps"].append({
                    "action": "insert",
                    "table": table,
                    "row_id": row_id,
                    "restore_data": "从备份恢复"
                })
                rollback["sql"].append(
                    f"-- 需要从备份恢复 {table} 表中 Id={row_id} 的数据"
                )

            elif operation == "insert":
                rollback["steps"].append({
                    "action": "delete",
                    "table": table,
                    "row_id": row_id,
                    "note": "删除新插入的行"
                })
                rollback["sql"].append(
                    f"DELETE FROM {table} WHERE Id = {row_id}"
                )

        # 生成 Python 回滚脚本
        if rollback["steps"]:
            script_lines = [
                "import openpyxl",
                "",
                f"def rollback_{table}():",
                f'    """回滚 {table} 表的变更"""',
                f'    wb = openpyxl.load_workbook("{table}.xlsx")',
                f"    sheet = wb.active",
                ""
            ]

            for step in rollback["steps"]:
                if step["action"] == "update":
                    script_lines.append(
                        f"    # 恢复 {step['field']} 的原值"
                    )
                    script_lines.append(
                        f"    # 找到 Id={step['row_id']} 的行，设置 {step['field']} = {step['restore_to']}"
                    )
                elif step["action"] == "delete":
                    script_lines.append(
                        f"    # 重新插入 Id={step['row_id']} 的数据"
                    )
                elif step["action"] == "insert":
                    script_lines.append(
                        f"    # 删除 Id={step['row_id']} 的新行"
                    )

            script_lines.extend([
                "",
                "    wb.save(f'{table}_rollback.xlsx')",
                '    print("回滚完成")'
            ])

            rollback["scripts"].append("\n".join(script_lines))

        return rollback

    def simulate_batch_changes(self, changes: List[Dict]) -> Dict[str, Any]:
        """模拟批量变更"""
        all_simulations = []

        for change_def in changes:
            table = change_def.get("table")
            table_changes = change_def.get("changes", [])

            sim = self.simulate_change(table, table_changes)
            all_simulations.append(sim)

        # 汇总所有模拟结果
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_changes": len(changes),
            "simulations": all_simulations,
            "overall_risk": self._calculate_overall_risk(all_simulations),
            "recommendations": self._generate_overall_recommendations(all_simulations)
        }

        return summary

    def _calculate_overall_risk(self, simulations: List[Dict]) -> str:
        """计算整体风险等级"""
        risk_scores = {"high": 3, "medium": 2, "low": 1, "none": 0}
        total_score = 0

        for sim in simulations:
            for risk in sim.get("risks", []):
                level = risk.get("level", "none")
                total_score += risk_scores.get(level, 0)

        if total_score >= 10:
            return "high"
        elif total_score >= 5:
            return "medium"
        elif total_score >= 1:
            return "low"
        else:
            return "none"

    def _generate_overall_recommendations(self, simulations: List[Dict]) -> List[str]:
        """生成整体建议"""
        recommendations = []

        total_indirect_impact = sum(len(sim.get("indirect_impact", [])) for sim in simulations)
        total_risks = sum(len(sim.get("risks", [])) for sim in simulations)

        if total_risks >= 5:
            recommendations.append("⚠️ 高风险变更：建议分阶段实施并充分测试")

        if total_indirect_impact > 20:
            recommendations.append(f"⚠️ 影响范围广：间接影响 {total_indirect_impact} 个表")

        center_tables = set()
        for sim in simulations:
            table = sim.get("table")
            if self._is_center_table(table):
                center_tables.add(table)

        if center_tables:
            recommendations.append(
                f"⚠️ 涉及中心表: {', '.join(center_tables)}，优先测试这些表的功能"
            )

        recommendations.append("建议执行前创建完整备份")
        recommendations.append("建议在测试环境先验证变更")

        return recommendations

    def load_relations(self, relations_file: str):
        """从文件加载关系"""
        with open(relations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.relations = data.get("relations", [])
        self._build_graph()

    def generate_report(self, simulation: Dict) -> str:
        """生成模拟报告"""
        is_batch = "simulations" in simulation

        if is_batch:
            return self._generate_batch_report(simulation)

        lines = [
            "# 配置变更模拟报告",
            f"",
            f"**模拟ID**: {simulation['simulation_id']}",
            f"**表**: {simulation['table']}",
            f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f""
        ]

        # 变更详情
        lines.extend([
            f"## 变更详情",
            f""
        ])

        for change in simulation["changes"]:
            operation = change.get("operation", "unknown")
            field = change.get("field", "")
            row_id = change.get("row_id")

            lines.append(f"- **操作**: {operation}")
            lines.append(f"  - 字段: {field}")
            if row_id:
                lines.append(f"  - 行ID: {row_id}")
            if "old_value" in change:
                lines.append(f"  - 原值: {change['old_value']}")
            if "new_value" in change:
                lines.append(f"  - 新值: {change['new_value']}")
            lines.append("")

        # 直接影响
        if simulation["direct_impact"]:
            lines.extend([
                f"## 直接影响",
                f""
            ])
            for impact in simulation["direct_impact"]:
                if impact.get("is_primary_key"):
                    lines.append(f"- ⚠️ 修改主键: {impact['field']}")
                elif impact.get("is_foreign_key"):
                    lines.append(f"- ⚠️ 修改外键: {impact['field']}")
                else:
                    lines.append(f"- 修改字段: {impact['field']}")

                if impact.get("affects_other_tables"):
                    lines.append(f"  - 影响表: {', '.join(impact['affects_other_tables'])}")
            lines.append("")

        # 间接影响
        if simulation["indirect_impact"]:
            lines.extend([
                f"## 间接影响",
                f""
            ])

            # 按距离分组
            by_distance = defaultdict(list)
            for imp in simulation["indirect_impact"]:
                by_distance[imp["distance"]].append(imp)

            for distance in sorted(by_distance.keys()):
                lines.append(f"### 距离 {distance}")
                for imp in by_distance[distance][:10]:
                    direction_icon = "➡️" if imp["direction"] == "forward" else "⬅️"
                    lines.append(f"- {direction_icon} {imp['table']}: {imp['path']}")
                lines.append("")

        # 风险评估
        if simulation["risks"]:
            lines.extend([
                f"## 风险评估",
                f""
            ])

            for risk in simulation["risks"]:
                level = risk.get("level", "unknown")
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
                lines.append(f"### {icon} {level.upper()} - {risk['type']}")
                lines.append(f"**描述**: {risk['message']}")
                lines.append(f"**建议**: {risk['suggestion']}")

                if risk.get("affected_tables"):
                    lines.append(f"**受影响表**: {', '.join(risk['affected_tables'])}")
                lines.append("")

        # 回滚方案
        if simulation["rollback"]:
            lines.extend([
                f"## 回滚方案",
                f""
            ])

            if simulation["rollback"]["steps"]:
                lines.extend([
                    f"### 回滚步骤",
                    f""
                ])
                for step in simulation["rollback"]["steps"]:
                    lines.append(f"- {step['action']}: {step.get('table', '')} {step.get('field', '')} = {step.get('restore_to', '')}")
                lines.append("")

        return "\n".join(lines)

    def _generate_batch_report(self, summary: Dict) -> str:
        """生成批量变更报告"""
        lines = [
            "# 批量配置变更模拟报告",
            f"",
            f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**总变更数**: {summary['total_changes']}",
            f"**整体风险**: {self._format_risk_level(summary['overall_risk'])}",
            f""
        ]

        # 建议
        if summary["recommendations"]:
            lines.extend([
                f"## 建议",
                f""
            ])
            for rec in summary["recommendations"]:
                lines.append(f"- {rec}")
            lines.append("")

        # 各个模拟
        lines.extend([
            f"## 各模拟详情",
            f""
        ])

        for sim in summary["simulations"]:
            lines.extend([
                f"### {sim['table']} ({sim['simulation_id']})",
                f"",
                f"- 变更数: {len(sim['changes'])}",
                f"- 直接影响: {len(sim['direct_impact'])}",
                f"- 间接影响: {len(sim['indirect_impact'])}",
                f"- 风险数: {len(sim['risks'])}",
                f""
            ])

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

    if len(sys.argv) < 2:
        print("用法:")
        print("  python simulator.py <关系文件.json> <变更定义.json> [输出文件]")
        print("")
        print("变更定义格式:")
        print('  单表变更:')
        print('  {')
        print('    "table": "Hero",')
        print('    "changes": [')
        print('      {"operation": "update", "field": "OpenDate", "row_id": 1001, "old_value": "2025-01-01", "new_value": "2025-01-02"}')
        print('    ]')
        print('  }')
        print("")
        print('  批量变更:')
        print('  [')
        print('    {"table": "Hero", "changes": [...]},')
        print('    {"table": "Skill", "changes": [...]}')
        print('  ]')
        sys.exit(1)

    relations_file = sys.argv[1]
    change_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "simulation_result.json"

    # 加载关系和变更
    with open(relations_file, 'r', encoding='utf-8') as f:
        relations_data = json.load(f)
        relations = relations_data.get("relations", [])

    with open(change_file, 'r', encoding='utf-8') as f:
        changes = json.load(f)

    simulator = ConfigSimulator(relations)

    # 执行模拟
    if isinstance(changes, list) and all("table" in c for c in changes):
        # 批量变更
        result = simulator.simulate_batch_changes(changes)
    else:
        # 单表变更
        table = changes.get("table")
        table_changes = changes.get("changes", [])
        result = simulator.simulate_change(table, table_changes)

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"模拟结果已保存到: {output_file}")

    # 生成报告
    report = simulator.generate_report(result)
    report_file = output_file.replace('.json', '_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已保存到: {report_file}")

    # 打印摘要
    print()
    if "overall_risk" in result:
        print(f"整体风险: {simulator._format_risk_level(result['overall_risk'])}")
    else:
        high_risks = [r for r in result.get("risks", []) if r.get("level") == "high"]
        print(f"高风险数: {len(high_risks)}")
    print(f"间接影响: {len(result.get('indirect_impact', []))} 个表")


if __name__ == "__main__":
    main()
