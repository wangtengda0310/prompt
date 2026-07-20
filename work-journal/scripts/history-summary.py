#!/usr/bin/env python3
"""
history-summary.py - 从 ~/.claude/history.jsonl 提取指定日期范围的用户对话摘要

用法:
    python history-summary.py                          # 今天
    python history-summary.py --date 2026-03-31        # 指定日期
    python history-summary.py --from 2026-03-25 --to 2026-03-31  # 日期范围
    python history-summary.py --week                   # 本周
    python history-summary.py --month                  # 本月

输出格式（每行一条）:
    HH:MM | 项目名 | 用户输入（截断到80字符）

退出码: 0=有数据, 1=无数据, 2=参数错误
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path


def get_history_path():
    """获取 history.jsonl 路径"""
    home = Path.home()
    return home / ".claude" / "history.jsonl"


def parse_ts(ts_ms):
    """将毫秒时间戳转为本地 datetime"""
    return datetime.fromtimestamp(ts_ms / 1000)


def filter_by_date(entries, date_str=None, from_str=None, to_str=None):
    """按日期过滤条目"""
    if date_str:
        target = date_str
        return [e for e in entries if parse_ts(e["timestamp"]).strftime("%Y-%m-%d") == target]

    results = entries
    if from_str:
        from_dt = datetime.strptime(from_str, "%Y-%m-%d")
        results = [e for e in results if parse_ts(e["timestamp"]) >= from_dt]
    if to_str:
        to_dt = datetime.strptime(to_str, "%Y-%m-%d") + timedelta(days=1)
        results = [e for e in results if parse_ts(e["timestamp"]) < to_dt]
    return results


def format_output(entries, max_display_len=80):
    """格式化输出"""
    lines = []
    for e in entries:
        dt = parse_ts(e["timestamp"])
        time_str = dt.strftime("%H:%M")
        project = os.path.basename(e.get("project", "?"))
        display = e.get("display", "").replace("\n", " ")[:max_display_len]
        lines.append(f"{time_str} | {project:20s} | {display}")
    return "\n".join(lines)


def get_date_range(period):
    """获取本周/本月的日期范围"""
    today = datetime.now()
    if period == "week":
        # ISO week: Monday is day 0
        monday = today - timedelta(days=today.weekday())
        return monday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    elif period == "month":
        first_of_month = today.replace(day=1)
        return first_of_month.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    return None, None


def main():
    parser = argparse.ArgumentParser(description="提取 Claude Code 历史对话摘要")
    parser.add_argument("--date", "-d", help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--from", dest="from_date", help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--week", "-w", action="store_true", help="本周")
    parser.add_argument("--month", "-m", action="store_true", help="本月")
    parser.add_argument("--max-len", type=int, default=80, help="截断显示长度 (默认80)")
    parser.add_argument("--project", "-p", help="按项目名过滤")
    parser.add_argument("--session", "-s", help="只显示指定 session ID 的条目")
    args = parser.parse_args()

    history_path = get_history_path()
    if not history_path.exists():
        print(f"错误: 找不到 {history_path}", file=sys.stderr)
        sys.exit(1)

    # 读取所有条目
    entries = []
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # 确定日期范围
    if args.date:
        filtered = filter_by_date(entries, date_str=args.date)
    elif args.week:
        from_d, to_d = get_date_range("week")
        filtered = filter_by_date(entries, from_str=from_d, to_str=to_d)
    elif args.month:
        from_d, to_d = get_date_range("month")
        filtered = filter_by_date(entries, from_str=from_d, to_str=to_d)
    elif args.from_date or args.to_date:
        filtered = filter_by_date(entries, from_str=args.from_date, to_str=args.to_date)
    else:
        # 默认: 今天
        today = datetime.now().strftime("%Y-%m-%d")
        filtered = filter_by_date(entries, date_str=today)

    # 按项目过滤
    if args.project:
        filtered = [e for e in filtered if args.project in e.get("project", "")]

    # 按 session 过滤
    if args.session:
        filtered = [e for e in filtered if e.get("sessionId") == args.session]

    if not filtered:
        print("无匹配记录", file=sys.stderr)
        sys.exit(1)

    # 输出统计信息
    dates = set(parse_ts(e["timestamp"]).strftime("%Y-%m-%d") for e in filtered)
    projects = set(os.path.basename(e.get("project", "?")) for e in filtered)
    sessions = set(e.get("sessionId", "?") for e in filtered)
    print(f"# 日期: {', '.join(sorted(dates))} | 条目: {len(filtered)} | 项目: {', '.join(sorted(projects))} | 会话: {len(sessions)}个", file=sys.stderr)

    # 输出格式化内容
    print(format_output(filtered, args.max_len))


if __name__ == "__main__":
    main()
