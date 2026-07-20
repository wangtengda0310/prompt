#!/usr/bin/env python3
"""
daily-review.py - 每日自动回顾分析脚本

分析指定日期的所有 Claude Code 会话，汇总统计信息。
从 ~/.claude/history.jsonl 读取会话入口，然后逐个分析会话文件。

用法:
    python daily-review.py                          # 分析昨天
    python daily-review.py --date 2026-04-01        # 指定日期
    python daily-review.py --output summary         # 简短文本输出
    python daily-review.py --no-cache               # 禁用缓存

退出码: 0=成功有数据, 1=无数据, 2=参数错误

Python module: daily-review (独立脚本，无外部依赖)
"""

import json
import os
import sys
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from itertools import islice
from pathlib import Path


# ─── 工具函数 ─────────────────────────────────────────────────────────

def get_history_path():
    """获取 ~/.claude/history.jsonl 路径"""
    return Path.home() / ".claude" / "history.jsonl"


def parse_ts_history(ts_ms):
    """将 history.jsonl 中的毫秒时间戳转为本地 datetime"""
    return datetime.fromtimestamp(ts_ms / 1000)


def parse_ts_session(ts_str):
    """将会话 .jsonl 中的 ISO 8601 字符串转为本地 datetime

    支持格式: '2026-03-24T03:35:52.886Z' (UTC)
    """
    if isinstance(ts_str, (int, float)):
        return datetime.fromtimestamp(ts_str / 1000)
    # 去掉末尾的 Z，按 UTC 解析后转为本地时间
    ts_str = ts_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts_str)
    if dt.tzinfo is not None:
        dt = dt.astimezone()
    return dt


def format_number(n):
    """格式化数字，大数使用 k/m 后缀"""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}m"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


# ─── 核心函数 ─────────────────────────────────────────────────────────

def get_target_date(args):
    """根据命令行参数确定目标日期

    支持:
    - 默认: yesterday
    - --yesterday: 昨天
    - --date YYYY-MM-DD: 指定日期
    """
    if args.date:
        try:
            return datetime.strptime(args.date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print(f"错误: 日期格式不正确 '{args.date}'，应为 YYYY-MM-DD", file=sys.stderr)
            sys.exit(2)
    # 默认分析昨天
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def load_history_entries(path, date_str):
    """流式读取 history.jsonl，按日期过滤

    逐行处理避免一次性加载到内存。
    """
    entries = []
    if not path.exists():
        return entries

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = entry.get("timestamp")
            if ts is None:
                continue

            entry_date = parse_ts_history(ts).strftime("%Y-%m-%d")
            if entry_date == date_str:
                entries.append(entry)

    return entries


def group_sessions(entries):
    """按 sessionId 分组历史条目

    返回: {session_id: [entry1, entry2, ...]}
    """
    groups = defaultdict(list)
    for entry in entries:
        sid = entry.get("sessionId")
        if sid:
            groups[sid].append(entry)
    return dict(groups)


def build_session_index(projects_dir):
    """预扫描 projects 目录，建立 session_id -> .jsonl 文件路径映射

    遍历 ~/.claude/projects/ 下的所有项目目录，
    收集所有 .jsonl 文件并按文件名（即 session_id）建立索引。
    """
    index = {}
    if not projects_dir.exists():
        return index

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            # 文件名就是 session_id
            session_id = jsonl_file.stem
            index[session_id] = jsonl_file

    return index


def analyze_session(session_file, session_id, history_entries):
    """分析单个会话文件

    流式逐行读取 .jsonl，统计:
    - token 用量（input/output）
    - 工具调用频次
    - Skill 调用详情
    - 错误检测
    - 会话时长
    - 每小时分布

    参数:
        session_file: 会话 .jsonl 文件路径
        session_id: 会话 ID
        history_entries: 该 session 在 history.jsonl 中的条目列表
    """
    result = {
        "session_id": session_id,
        "project": None,
        "project_dir": None,
        "start_time": None,
        "end_time": None,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "zero_usage_count": 0,
        "tool_usage": Counter(),
        "skill_calls": [],
        "errors": [],
        "user_turns": 0,
        "assistant_turns": 0,
        "tool_sequence": [],  # 用于检测工具组合模式
        "models_used": set(),
        "first_display": None,
        "git_branch": None,
    }

    # 从 history 条目提取项目信息和首个用户输入
    if history_entries:
        first_entry = history_entries[0]
        result["project"] = os.path.basename(first_entry.get("project", "unknown"))
        result["project_dir"] = first_entry.get("project")
        result["first_display"] = first_entry.get("display", "")
        # 从最后一个条目获取 git branch（如果有的话）

    if not session_file or not session_file.exists():
        return result

    # 跨消息的工具调用序列（按时间顺序）
    cross_msg_tools = []

    with open(session_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            record_type = record.get("type")
            if record_type not in ("user", "assistant"):
                continue

            # 解析时间戳
            ts = record.get("timestamp")
            if ts:
                try:
                    dt = parse_ts_session(ts)
                    if result["start_time"] is None or dt < result["start_time"]:
                        result["start_time"] = dt
                    if result["end_time"] is None or dt > result["end_time"]:
                        result["end_time"] = dt
                except (ValueError, TypeError):
                    pass

            # 提取 git branch
            git_branch = record.get("gitBranch")
            if git_branch:
                result["git_branch"] = git_branch

            message = record.get("message", {})
            if not message:
                continue

            # ── 处理 user 消息 ──
            if record_type == "user":
                result["user_turns"] += 1
                content = message.get("content")

                # 检测 tool_result 中的错误
                if isinstance(content, list):
                    for block in content:
                        if (isinstance(block, dict)
                                and block.get("type") == "tool_result"
                                and block.get("is_error") is True):
                            error_msg = block.get("content", "")
                            # 截断过长错误消息
                            if isinstance(error_msg, str) and len(error_msg) > 200:
                                error_msg = error_msg[:200] + "..."
                            result["errors"].append({
                                "tool_use_id": block.get("tool_use_id", ""),
                                "error": error_msg,
                            })
                continue

            # ── 处理 assistant 消息 ──
            if record_type == "assistant":
                result["assistant_turns"] += 1
                model = message.get("model")
                if model:
                    result["models_used"].add(model)

                # 统计 token 用量
                usage = message.get("usage", {})
                if usage:
                    input_tokens = usage.get("input_tokens", 0) or 0
                    output_tokens = usage.get("output_tokens", 0) or 0
                    result["total_input_tokens"] += input_tokens
                    result["total_output_tokens"] += output_tokens

                    # glm 模型有时 usage 全为 0，记录此类情况
                    if input_tokens == 0 and output_tokens == 0:
                        result["zero_usage_count"] += 1

                # 分析 content 数组中的工具调用
                content = message.get("content")
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        block_type = block.get("type")

                        # 检测 tool_use 和 server_tool_use
                        if block_type in ("tool_use", "server_tool_use"):
                            tool_name = block.get("name", "")
                            if tool_name:
                                result["tool_usage"][tool_name] += 1
                                # 追加到跨消息序列
                                cross_msg_tools.append(tool_name)

                            # 检测 Skill 调用
                            if tool_name == "Skill":
                                tool_input = block.get("input", {})
                                skill_name = tool_input.get("skill", "unknown")
                                skill_args = tool_input.get("args", "")
                                result["skill_calls"].append({
                                    "skill": skill_name,
                                    "args": skill_args[:100] if skill_args else "",
                                })

    # 将跨消息工具序列存入结果
    result["tool_sequence"] = cross_msg_tools

    # 计算会话时长（分钟）
    if result["start_time"] and result["end_time"]:
        duration = (result["end_time"] - result["start_time"]).total_seconds() / 60
        result["duration_minutes"] = round(duration, 1)
    else:
        result["duration_minutes"] = 0

    return result


def extract_tool_patterns(analyses, min_count=3):
    """检测跨会话重复的工具组合模式

    将每个会话中的工具调用序列提取为 2-gram 和 3-gram，
    统计出现频次 >= min_count 的模式。

    参数:
        analyses: 所有会话的分析结果列表
        min_count: 最低出现次数阈值
    """
    pattern_counter = Counter()

    for analysis in analyses:
        tool_seq = analysis.get("tool_sequence", [])
        if not tool_seq:
            continue
        # 提取 2-gram 和 3-gram
        for n in (2, 3):
            for i in range(len(tool_seq) - n + 1):
                pattern = tuple(tool_seq[i:i + n])
                pattern_counter[pattern] += 1

    # 过滤低频模式，按频次排序
    result = []
    for pattern, count in pattern_counter.most_common(20):
        if count >= min_count:
            result.append({
                "pattern": list(pattern),
                "count": count,
            })

    return result


def aggregate_stats(analyses):
    """汇总所有会话的统计数据

    返回: 包含所有汇总指标的字典
    """
    total_sessions = len(analyses)
    sessions_with_files = sum(1 for a in analyses if a.get("tool_usage"))
    total_input = sum(a.get("total_input_tokens", 0) for a in analyses)
    total_output = sum(a.get("total_output_tokens", 0) for a in analyses)
    total_zero = sum(a.get("zero_usage_count", 0) for a in analyses)
    total_user_turns = sum(a.get("user_turns", 0) for a in analyses)
    total_assistant_turns = sum(a.get("assistant_turns", 0) for a in analyses)

    # 工具使用汇总
    tool_summary = Counter()
    for a in analyses:
        tool_summary.update(a.get("tool_usage", {}))

    # Skill 使用汇总
    skill_summary = defaultdict(lambda: {"count": 0, "sessions": set()})
    for a in analyses:
        sid = a.get("session_id", "")
        for sc in a.get("skill_calls", []):
            skill_name = sc["skill"]
            skill_summary[skill_name]["count"] += 1
            skill_summary[skill_name]["sessions"].add(sid)

    # 将 set 转为 list 以便 JSON 序列化
    skill_summary_serializable = {}
    for name, info in skill_summary.items():
        skill_summary_serializable[name] = {
            "count": info["count"],
            "sessions": list(info["sessions"]),
        }

    # 项目分布
    project_dist = defaultdict(lambda: {"sessions": 0, "input_tokens": 0, "output_tokens": 0})
    for a in analyses:
        proj = a.get("project") or "unknown"
        project_dist[proj]["sessions"] += 1
        project_dist[proj]["input_tokens"] += a.get("total_input_tokens", 0)
        project_dist[proj]["output_tokens"] += a.get("total_output_tokens", 0)

    # 每小时会话分布（基于会话开始时间）
    hour_dist = Counter()
    for a in analyses:
        start = a.get("start_time")
        if start:
            hour_dist[str(start.hour)] += 1

    # 平均轮次
    avg_turns = round(total_user_turns / total_sessions, 1) if total_sessions > 0 else 0

    # 所有错误汇总
    all_errors = []
    for a in analyses:
        for err in a.get("errors", []):
            all_errors.append({
                "session": a.get("session_id", ""),
                "project": a.get("project", ""),
                "error": err["error"],
            })

    # 工具模式
    tool_patterns = extract_tool_patterns(analyses)

    return {
        "total_sessions": total_sessions,
        "sessions_with_files": sessions_with_files,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "zero_usage_count": total_zero,
        "total_user_turns": total_user_turns,
        "total_assistant_turns": total_assistant_turns,
        "avg_turns_per_session": avg_turns,
        "tool_usage_summary": dict(tool_summary.most_common()),
        "skill_usage_summary": skill_summary_serializable,
        "project_distribution": dict(project_dist),
        "sessions_by_hour": dict(sorted(hour_dist.items())),
        "tool_patterns": tool_patterns,
        "errors": all_errors,
    }


def update_trends(trends_path, date_str, stats):
    """追加趋势数据到 trends.json

    保留最近 30 天的数据，淘汰更旧数据。
    """
    trends = {}
    if trends_path.exists():
        try:
            with open(trends_path, "r", encoding="utf-8") as f:
                trends = json.load(f)
        except (json.JSONDecodeError, OSError):
            trends = {}

    # 添加当天数据
    trends[date_str] = {
        "total_sessions": stats["total_sessions"],
        "total_input_tokens": stats["total_input_tokens"],
        "total_output_tokens": stats["total_output_tokens"],
        "total_user_turns": stats["total_user_turns"],
        "tool_count": sum(stats["tool_usage_summary"].values()),
        "error_count": len(stats["errors"]),
    }

    # 保留最近 30 天
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    trends = {k: v for k, v in trends.items() if k >= cutoff}

    trends_path.parent.mkdir(parents=True, exist_ok=True)
    with open(trends_path, "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2, ensure_ascii=False)

    return trends


def compute_comparisons(date_str, stats, trends):
    """计算环比数据

    与前一天对比，以及与 7 天均值对比。
    """
    current_date = datetime.strptime(date_str, "%Y-%m-%d")
    yesterday = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # 7 天日期列表（不含当天）
    seven_day_dates = []
    for i in range(1, 8):
        d = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
        seven_day_dates.append(d)

    comparisons = {"vs_yesterday": None, "vs_7day_avg": None}

    # 与前一天对比
    yesterday_data = trends.get(yesterday)
    if yesterday_data:
        comparisons["vs_yesterday"] = _calc_delta(stats, yesterday_data)

    # 与 7 天均值对比
    seven_day_data = [trends[d] for d in seven_day_dates if d in trends]
    if seven_day_data:
        avg_data = {
            "total_sessions": sum(d["total_sessions"] for d in seven_day_data) / len(seven_day_data),
            "total_input_tokens": sum(d["total_input_tokens"] for d in seven_day_data) / len(seven_day_data),
            "total_output_tokens": sum(d["total_output_tokens"] for d in seven_day_data) / len(seven_day_data),
            "total_user_turns": sum(d["total_user_turns"] for d in seven_day_data) / len(seven_day_data),
            "tool_count": sum(d["tool_count"] for d in seven_day_data) / len(seven_day_data),
            "error_count": sum(d["error_count"] for d in seven_day_data) / len(seven_day_data),
        }
        comparisons["vs_7day_avg"] = _calc_delta(stats, avg_data)

    return comparisons


def _calc_delta(current, baseline):
    """计算当前数据与基准的百分比变化"""
    deltas = {}
    for key in ("total_sessions", "total_input_tokens", "total_output_tokens",
                "total_user_turns", "tool_count", "error_count"):
        cur = current.get(key, 0)
        base = baseline.get(key, 0)
        if base > 0:
            deltas[key] = round((cur - base) / base * 100, 1)
        elif cur > 0:
            deltas[key] = 100.0  # 从 0 增长视为 +100%
        else:
            deltas[key] = 0.0
    return deltas


def format_session_for_output(analysis):
    """将单个会话分析结果格式化为可序列化的字典"""
    return {
        "session_id": analysis["session_id"],
        "project": analysis.get("project"),
        "first_display": analysis.get("first_display", "")[:80],
        "git_branch": analysis.get("git_branch"),
        "start_time": analysis["start_time"].isoformat() if analysis.get("start_time") else None,
        "end_time": analysis["end_time"].isoformat() if analysis.get("end_time") else None,
        "duration_minutes": analysis.get("duration_minutes", 0),
        "user_turns": analysis.get("user_turns", 0),
        "assistant_turns": analysis.get("assistant_turns", 0),
        "total_input_tokens": analysis.get("total_input_tokens", 0),
        "total_output_tokens": analysis.get("total_output_tokens", 0),
        "zero_usage_count": analysis.get("zero_usage_count", 0),
        "tool_usage": dict(analysis.get("tool_usage", {})),
        "skill_calls": analysis.get("skill_calls", []),
        "errors": analysis.get("errors", []),
        "models_used": list(analysis.get("models_used", set())),
    }


def format_summary_text(stats, date_str, comparisons):
    """将统计数据格式化为简短的文本摘要"""
    lines = [
        f"=== 每日回顾: {date_str} ===",
        f"会话数: {stats['total_sessions']}  "
        f"(有工具使用: {stats['sessions_with_files']})",
        f"Token: 输入 {format_number(stats['total_input_tokens'])}  "
        f"输出 {format_number(stats['total_output_tokens'])}  "
        f"(零用量 {stats['zero_usage_count']} 次)",
        f"轮次: 用户 {stats['total_user_turns']}  "
        f"助手 {stats['total_assistant_turns']}  "
        f"平均 {stats['avg_turns_per_session']}/会话",
        f"错误: {len(stats['errors'])} 个",
    ]

    # 工具 Top5
    if stats["tool_usage_summary"]:
        top_tools = list(stats["tool_usage_summary"].items())[:5]
        tools_str = "  ".join(f"{name}({count})" for name, count in top_tools)
        lines.append(f"工具 Top5: {tools_str}")

    # Skill 使用
    if stats["skill_usage_summary"]:
        for name, info in stats["skill_usage_summary"].items():
            lines.append(f"Skill: {name} - {info['count']}次 ({len(info['sessions'])}个会话)")

    # 项目分布
    if stats["project_distribution"]:
        for proj, info in stats["project_distribution"].items():
            lines.append(f"项目: {proj} - {info['sessions']}个会话")

    # 环比
    if comparisons.get("vs_yesterday"):
        vy = comparisons["vs_yesterday"]
        lines.append(f"环比昨天: 会话 {vy['total_sessions']:+.0f}%  "
                      f"Token {vy['total_input_tokens']:+.0f}%  "
                      f"错误 {vy['error_count']:+.0f}%")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="每日回顾分析 - 分析指定日期的 Claude Code 会话统计",
    )
    parser.add_argument(
        "--date", "-d",
        help="指定日期 (YYYY-MM-DD)，默认分析昨天",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["json", "summary"],
        default="json",
        help="输出格式: json(完整JSON) 或 summary(简短文本)，默认 json",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="禁用缓存（默认启用缓存）",
    )
    args = parser.parse_args()

    # 确定目标日期
    date_str = get_target_date(args)

    # 缓存路径
    skill_dir = Path(__file__).resolve().parent.parent
    cache_dir = skill_dir / "cache"
    cache_file = cache_dir / f"{date_str}.json"
    trends_path = cache_dir / "trends.json"

    # 检查缓存
    if not args.no_cache and cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if args.output == "summary":
            comparisons = cached.get("comparisons", {})
            print(format_summary_text(cached, date_str, comparisons))
        else:
            print(json.dumps(cached, indent=2, ensure_ascii=False))
        sys.exit(0)

    # 读取 history.jsonl
    history_path = get_history_path()
    if not history_path.exists():
        print(f"错误: 找不到 {history_path}", file=sys.stderr)
        sys.exit(1)

    entries = load_history_entries(history_path, date_str)
    if not entries:
        print(f"无 {date_str} 的会话记录", file=sys.stderr)
        sys.exit(1)

    # 按 session 分组
    session_groups = group_sessions(entries)

    # 建立会话文件索引
    projects_dir = Path.home() / ".claude" / "projects"
    session_index = build_session_index(projects_dir)

    # 逐个分析会话
    analyses = []
    for session_id, history_entries in session_groups.items():
        session_file = session_index.get(session_id)
        analysis = analyze_session(session_file, session_id, history_entries)
        analyses.append(analysis)

    # 汇总统计
    stats = aggregate_stats(analyses)

    # 更新趋势数据
    trends = update_trends(trends_path, date_str, stats)

    # 计算环比
    comparisons = compute_comparisons(date_str, stats, trends)

    # 构建完整输出
    output = {
        "date": date_str,
        **stats,
        "comparisons": comparisons,
        "sessions": [format_session_for_output(a) for a in analyses],
    }

    # 写入缓存
    if not args.no_cache:
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    # 输出结果
    if args.output == "summary":
        print(format_summary_text(stats, date_str, comparisons))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
