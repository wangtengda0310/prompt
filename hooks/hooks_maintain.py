#!/usr/bin/env python3
"""hooks_maintain: PostToolUse 提醒 — Read/Edit/Write 触碰 ~/.claude/hooks/ 下文件时注入维护 checklist。

目的: 防止"改完本机 hook 忘了回写共享包 / 更新 forgetful" (2026-09-30 实际发生:
Windows 适配修复后靠用户提醒才补全 #466, 遂建此机制)。
Read 也触发: 改动前的研读阶段就可见 checklist, 提醒更早。
详细文档: 同目录 CLAUDE.md (hooks 维护纪律); 该文件在项目树外不会自动进上下文,
靠本 hook 的注入指引读取。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_stdin_json

HOOKS_DIR = os.path.dirname(os.path.realpath(__file__))

CHECKLIST = (
    "[hooks-maintain] 触碰了本机 hook 脚本。若是改动, 收尾 checklist "
    "(详细版见 ~/.claude/hooks/CLAUDE.md):\n"
    "1. 冒烟: 管道喂 JSON 验证行为 (PS 5.1 须先 $OutputEncoding=[Text.Encoding]::UTF8,\n"
    "   且管道会带双 BOM — common.read_stdin_json 已剥离; 完整坑列表见 CLAUDE.md)\n"
    "2. scp 回写共享包 (唯一权威源码):\n"
    "   scp <改的文件> FORGETFUL_USER@FORGETFUL_HOST:forgetful-share/claude-code-share/hooks/\n"
    "3. 登记共享包 CHANGELOG.md (日期/机器/改了什么; forgetful 记为什么, CHANGELOG 记改什么)\n"
    "4. forgetful 分层记忆 (update 原条目勿建平行条目, #455 纪律):\n"
    "   通用缺陷/组件变化→#466 | 本机事实→#467 | API 映射层→#465\n"
    "5. 提醒用户: 其他机器可从 share 拉取更新"
)


def cmd_posttool():
    ev = read_stdin_json()
    ti = ev.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    try:
        # 只对本 hooks 目录下的文件触发 (realpath 归一后前缀匹配)
        if path and os.path.realpath(path).startswith(HOOKS_DIR + os.sep):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": CHECKLIST,
                }
            }, ensure_ascii=False))
    except Exception:
        pass  # 提醒失败绝不阻塞
    sys.exit(0)


if __name__ == "__main__":
    {"posttool": cmd_posttool}[sys.argv[1] if len(sys.argv) > 1 else "posttool"]()
