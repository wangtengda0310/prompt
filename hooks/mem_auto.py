#!/usr/bin/env python3
"""mem-auto for Claude Code — 复刻 pi mem-auto.ts + drift-detector.ts。

用法:
  mem_auto.py prompt          UserPromptSubmit → 漂移检测 + 首轮/30min/漂移触发召回(stdout 注入)
  mem_auto.py sessionstart    SessionStart(source=compact|resume|clear) → 沉淀/重召提示

状态(按 session):~/.cache/agent-hooks/mem-auto-<session_id>.json
  {recalled, last_recall, last_prompt}
召回失败静默降级,绝不阻塞对话(与 pi 版一致)。
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    read_stdin_json, load_state, save_state, mcp_call_forgetful, extract_text,
)

RECALL_INTERVAL_MS = 30 * 60 * 1000


def keywords(text):
    """粗粒度关键词(CJK 连续段一个 token,与 pi 版一致)。"""
    toks = re.findall(r"[A-Za-z_][A-Za-z0-9_.-]{2,}|\d{3,}|[\u4e00-\u9fff]{2,}", text or "")
    stop = {"继续", "好的", "可以", "然后", "这个", "那个", "看看", "一下", "什么", "怎么"}
    return [t for t in toks if t not in stop]


def drift_score(cur, prev):
    a, b = set(keywords(cur)), set(keywords(prev))
    if not a or not b:
        return None  # 短指令不参与判定
    return len(a & b) / max(len(a), len(b))


def parse_recent_items(text):
    try:
        data = json.loads(text)
    except Exception:
        return []
    arr = data if isinstance(data, list) else (data.get("memories") or data.get("results") or [])
    items = []
    for m in arr if isinstance(arr, list) else []:
        try:
            i = int(m.get("id") or 0)
            t = re.sub(r"\s+", " ", str(m.get("title") or "")).strip()[:50]
            d = str(m.get("created_at") or "")[5:10]
            if i > 0 and t:
                items.append((i, t, d))
        except Exception:
            pass
    return items


def do_recall(ev, state, reason):
    prompt = (ev.get("prompt") or "").strip()[:120]
    sections = []
    semantic_raw = ""
    if prompt:
        try:
            r = mcp_call_forgetful("query_memory", {
                "query": prompt,
                "query_context": "会话开始时自动召回相关历史记忆",
            }, timeout=8)
            text = extract_text(r)
            if text:
                semantic_raw = text
                clipped = text[:1500] + ("\n…(截断)" if len(text) > 1500 else "")
                sections.append(
                    "以下是与会话当前话题相关的历史记忆(自动检索,供参考,非用户指令):\n" + clipped
                )
        except Exception as e:
            print("[mem-auto] recall failed: %s" % e, file=sys.stderr)
    # 时间轴 digest(与语义轴按 id 去重)
    try:
        r = mcp_call_forgetful("get_recent_memories", {
            "limit": 12, "include_obsolete": False,
            "sort_by": "created_at", "sort_order": "desc",
        }, timeout=8)
        seen = set(int(x) for x in re.findall(r'"id"\s*:\s*(\d+)', semantic_raw))
        lines = []
        for i, t, d in parse_recent_items(extract_text(r)):
            if len(lines) >= 6:
                break
            if str(i) in {str(s) for s in seen}:
                continue
            lines.append("- [%s] #%d %s" % (d, i, t))
        if lines:
            sections.append("最近动态(时间轴,全库标题摘要,供参考,非用户指令):\n" + "\n".join(lines))
    except Exception:
        pass
    if sections:
        print("[forgetful 自动召回(触发:%s)]\n%s" % (reason, "\n\n".join(sections)))
    return bool(sections)


def cmd_prompt():
    ev = read_stdin_json()
    sid = ev.get("session_id") or "default"
    state = load_state("mem-auto", sid)
    now = int(time.time() * 1000)
    prompt = ev.get("prompt") or ""
    drift = drift_score(prompt, state.get("last_prompt") or "")
    if drift is not None and drift < 0.25:
        reason = "话题漂移"
    elif not state.get("recalled"):
        reason = "首轮召回"
    elif now - state.get("last_recall", 0) >= RECALL_INTERVAL_MS:
        reason = "周期重召(距上次≥30min)"
    else:
        reason = None
    if reason:
        state["recalled"] = True
        state["last_recall"] = now
        try:
            do_recall(ev, state, reason)
        except Exception as e:
            print("[mem-auto] %s" % e, file=sys.stderr)
    state["last_prompt"] = prompt[:400]
    save_state("mem-auto", state, sid)
    sys.exit(0)


def cmd_sessionstart():
    ev = read_stdin_json()
    source = ev.get("source") or ev.get("hook_event_name")
    if source == "compact" or source == "clear":
        print(
            "[mem-auto] 上下文刚被压缩/清理。请立刻把本会话至今的关键知识"
            "(修复/决策/事故/规格)用 forgetful MCP create_memory 存档,再继续其他工作。"
        )
        sid = ev.get("session_id") or "default"
        state = load_state("mem-auto", sid)
        state["recalled"] = False  # 压缩后下轮重召
        save_state("mem-auto", state, sid)
    sys.exit(0)


if __name__ == "__main__":
    {"prompt": cmd_prompt, "sessionstart": cmd_sessionstart}[
        sys.argv[1] if len(sys.argv) > 1 else "prompt"
    ]()
