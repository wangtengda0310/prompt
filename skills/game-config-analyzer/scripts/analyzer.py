#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配表分析辅助脚本

用于扫描配表文件、分析关系、生成报告
"""

import openpyxl
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict


class ConfigAnalyzer:
    """配表分析器"""

    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.tables = {}  # {filename: {sheets, structure}}
        self.relations = []  # 关系列表
        self.constraints = []  # 约束列表

    def scan_directory(self) -> Dict[str, Any]:
        """扫描目录，收集所有配表文件"""
        result = {
            "files": [],
            "total_count": 0,
            "sheets_count": 0
        }

        for file_path in self.config_dir.rglob("*.xlsx"):
            # 跳过临时文件
            if "~$" in file_path.name:
                continue

            file_info = self._analyze_file(file_path)
            if file_info:
                result["files"].append(file_info)
                result["total_count"] += 1
                result["sheets_count"] += len(file_info["sheets"])

        return result

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            wb = openpyxl.load_workbook(file_path, data_only=False)
            sheets = []

            for sheet in wb.worksheets:
                sheet_info = self._analyze_sheet(sheet)
                if sheet_info:
                    sheets.append(sheet_info)

            if not sheets:
                return None

            return {
                "filename": file_path.name,
                "path": str(file_path),
                "sheets": sheets
            }
        except Exception as e:
            print(f"警告: 无法读取 {file_path}: {e}")
            return None

    def _analyze_sheet(self, sheet) -> Dict[str, Any]:
        """分析单个 Sheet"""
        # 找到数据起始行
        header_row = self._find_header_row(sheet)
        if header_row is None:
            return None

        # 提取表头信息
        headers = self._extract_headers(sheet, header_row)
        if not headers:
            return None

        # 统计数据行数
        data_start_row = header_row + 1
        data_rows = 0
        for row in sheet.iter_rows(min_row=data_start_row, values_only=True):
            if row and any(cell is not None for cell in row):
                data_rows += 1

        return {
            "name": sheet.title,
            "headers": headers,
            "row_count": data_rows,
            "header_row": header_row
        }

    def _find_header_row(self, sheet) -> int:
        """查找表头行（包含字段名的那一行）"""
        for row_idx in range(1, 10):
            # 第4行通常是字段名行
            if row_idx == 4:
                return row_idx
            # 检查是否有 server/client 标记
            for cell in sheet[row_idx]:
                if cell.value and 'server/client' in str(cell.value):
                    return row_idx - 1  # 字段名在上一行
        return 4  # 默认第4行

    def _extract_headers(self, sheet, header_row: int) -> List[Dict[str, Any]]:
        """提取表头信息"""
        headers = []

        for col_idx in range(1, sheet.max_column + 1):
            chs_name = sheet.cell(1, col_idx).value  # 中文名
            field_type = sheet.cell(2, col_idx).value  # 类型
            field_name = sheet.cell(header_row, col_idx).value  # 字段名
            export_tag = sheet.cell(header_row + 1, col_idx).value  # 导出标识

            if not field_name:
                continue

            headers.append({
                "column": col_idx,
                "chs_name": str(chs_name) if chs_name else "",
                "type": str(field_type) if field_type else "",
                "name": str(field_name),
                "export": str(export_tag) if export_tag else ""
            })

        return headers

    def analyze_relations(self, scan_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析表之间的引用关系"""
        relations = []

        # 构建表名到文件的映射
        table_map = {}
        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                table_name = sheet_info["name"].replace(".xlsx", "")
                table_map[table_name] = {
                    "file": file_info["filename"],
                    "sheet": sheet_info["name"],
                    "headers": sheet_info["headers"]
                }

        # 分析 ID 引用关系
        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                for header in sheet_info["headers"]:
                    relations.extend(self._find_id_references(
                        header, sheet_info, table_map
                    ))

        return relations

    def _find_id_references(self, header: Dict, sheet_info: Dict, table_map: Dict) -> List[Dict]:
        """查找 ID 引用关系"""
        relations = []
        field_name = header["name"]

        # 模式1: XxxId -> Xxx.Id
        id_match = re.match(r'(.+)Id$', field_name)
        if id_match:
            ref_table = id_match.group(1)
            if ref_table in table_map:
                relations.append({
                    "source_table": sheet_info["name"],
                    "source_field": field_name,
                    "target_table": ref_table,
                    "target_field": "Id",
                    "type": "id_reference"
                })

        # 模式2: XxxIds -> Xxx.Id (数组引用)
        ids_match = re.match(r'(.+)Ids$', field_name)
        if ids_match:
            ref_table = ids_match.group(1)
            if ref_table in table_map:
                relations.append({
                    "source_table": sheet_info["name"],
                    "source_field": field_name,
                    "target_table": ref_table,
                    "target_field": "Id",
                    "type": "id_array_reference"
                })

        return relations

    def extract_constraints(self, scan_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取约束规则"""
        constraints = []

        for file_info in scan_result["files"]:
            for sheet_info in file_info["sheets"]:
                constraints.extend(self._extract_sheet_constraints(sheet_info))

        return constraints

    def _extract_sheet_constraints(self, sheet_info: Dict) -> List[Dict]:
        """提取 Sheet 级别的约束"""
        constraints = []
        headers = sheet_info["headers"]
        sheet_name = sheet_info["name"]

        # 查找时间相关字段
        time_fields = {}
        for header in headers:
            name = header["name"].lower()
            if any(kw in name for kw in ['time', 'date', 'start', 'end']):
                time_fields[header["name"]] = header

        # 时间顺序约束
        if "StartTime" in time_fields and "EndTime" in time_fields:
            constraints.append({
                "table": sheet_name,
                "constraint_type": "time_order",
                "rule": "StartTime < EndTime",
                "fields": ["StartTime", "EndTime"]
            })

        # 时间范围约束
        if "OpenDate" in time_fields:
            constraints.append({
                "table": sheet_name,
                "constraint_type": "opendate_requirement",
                "rule": "IsOpen=true 时 OpenDate 必须有值",
                "fields": ["OpenDate", "IsOpen"]
            })

        return constraints

    def generate_mermaid_graph(self, relations: List[Dict]) -> str:
        """生成 Mermaid 关系图"""
        lines = ["graph TD"]

        # 收集所有节点
        nodes = set()
        for rel in relations:
            nodes.add(rel["source_table"])
            nodes.add(rel["target_table"])

        # 生成节点
        for node in sorted(nodes):
            lines.append(f'    {node}[{node}]')

        # 生成关系
        for rel in relations:
            style = ""
            if rel["type"] == "id_array_reference":
                style = " -.->|数组引用|"
            else:
                style = " -->|引用|"
            lines.append(f'    {rel["source_table"]}{style}{rel["target_table"]}')

        return "\n".join(lines)

    def generate_test_data_template(self, scan_result: Dict) -> str:
        """生成测试数据模板"""
        template = """# 测试用例模板

## 测试场景矩阵

| 场景ID | 表名 | 字段 | 测试值 | 期望结果 |
|--------|------|------|--------|----------|
"""

        return template


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python analyzer.py <配表目录>")
        sys.exit(1)

    config_dir = sys.argv[1]
    analyzer = ConfigAnalyzer(config_dir)

    # 扫描配表
    print("扫描配表...")
    scan_result = analyzer.scan_directory()
    print(f"找到 {scan_result['total_count']} 个文件, {scan_result['sheets_count']} 个 Sheet")

    # 分析关系
    print("分析关系...")
    relations = analyzer.analyze_relations(scan_result)
    print(f"找到 {len(relations)} 个引用关系")

    # 提取约束
    print("提取约束...")
    constraints = analyzer.extract_constraints(scan_result)
    print(f"找到 {len(constraints)} 个约束规则")

    # 生成图表
    mermaid = analyzer.generate_mermaid_graph(relations)
    print("\nMermaid 图表:")
    print(mermaid)

    # 保存结果
    output = {
        "scan_result": scan_result,
        "relations": relations,
        "constraints": constraints,
        "mermaid_graph": mermaid
    }

    output_file = "config_analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
