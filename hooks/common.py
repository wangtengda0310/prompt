#!/usr/bin/env python3
"""agent-hooks 共享库:stdin JSON 解析 / forgetful MCP-over-HTTP 客户端 / 状态文件。
复刻自 pi 的 mem-auto.ts 配置驱动模式:服务地址读 ~/.config/mcp/mcp.json。
macOS 自带 python3.9 兼容,零第三方依赖。
"""
import json
import os
import sys
import urllib.request

# Windows 编码坑 (2026-09-30 LOCAL_HOSTNAME 实测, 与 statusline 的 GBK stdin 坑同源):
# Claude Code 给 hook 的 stdin 是 UTF-8 JSON, stdout 注入也按 UTF-8 解读;
# 而 Windows Python 默认按 locale (中文系统=GBK) 编解码管道 => 中文 prompt 乱码 =>
# json.loads 失败被 read_stdin_json 吞成 {} => hook 静默失效 (无报错无输出)。
# 强制三流 UTF-8; Mac/Linux 默认已是 UTF-8, 此处为无害空操作。
try:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

HOOK_STATE_DIR = os.path.expanduser("~/.cache/agent-hooks")
DEFAULT_URL = "http://FORGETFUL_HOST:8020/mcp"


def read_stdin_json():
    """Claude Code hook 协议:JSON 从 stdin 进来。失败返回 {}。
    容错:剥离 UTF-8 BOM —— PS 5.1 管道测试会带入 (实测 ﻿﻿ 双 BOM 致
    json.loads 抛 JSONDecodeError 被吞成 {}, hook 静默失效); Claude Code 真实输入无 BOM。"""
    try:
        raw = sys.stdin.read() or "{}"
        return json.loads(raw.lstrip("﻿"))
    except Exception:
        return {}


def forgetful_url():
    """与 pi 扩展同源:~/.config/mcp/mcp.json 的 mcpServers.forgetful.url。"""
    try:
        with open(os.path.expanduser("~/.config/mcp/mcp.json")) as f:
            url = json.load(f)["mcpServers"]["forgetful"]["url"]
        if isinstance(url, str) and url.startswith("http"):
            return url
    except Exception:
        pass
    return os.environ.get("FORGETFUL_URL", DEFAULT_URL)


def _session_cache_path():
    return os.path.join(HOOK_STATE_DIR, "mcp-session.json")


def _load_sid():
    try:
        with open(_session_cache_path()) as f:
            d = json.load(f)
        if d.get("url") == forgetful_url() and d.get("sid"):
            return d["sid"]
    except Exception:
        pass
    return None


def _save_sid(sid):
    os.makedirs(HOOK_STATE_DIR, exist_ok=True)
    with open(_session_cache_path(), "w") as f:
        json.dump({"url": forgetful_url(), "sid": sid}, f)


def _post(body, sid=None, timeout=10):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if sid:
        headers["mcp-session-id"] = sid
    req = urllib.request.Request(
        forgetful_url(), data=json.dumps(body).encode(), headers=headers
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    text = resp.read().decode()
    new_sid = resp.headers.get("mcp-session-id")
    msg = None
    for line in text.split("\n"):
        if line.startswith("data: "):
            msg = json.loads(line[6:])
            break
    if msg is None:
        msg = json.loads(text)
    return new_sid, msg, resp.status


def mcp_call_forgetful(tool_name, arguments, timeout=10):
    """完整链路:init(带缓存)→ tools/call(execute_forgetful_tool)→ result。"""
    sid = _load_sid()
    if not sid:
        new_sid, _, _ = _post(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "claude-agent-hooks", "version": "1.0"},
                },
            },
            timeout=timeout,
        )
        if not new_sid:
            raise RuntimeError("mcp init: no session id")
        sid = new_sid
        _save_sid(sid)
        try:
            _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid=sid)
        except Exception:
            pass
    body = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "execute_forgetful_tool",
            "arguments": {"tool_name": tool_name, "arguments": arguments},
        },
    }
    _, m, status = _post(body, sid=sid, timeout=timeout)
    if status == 404:  # 会话过期:重建一次
        os.remove(_session_cache_path())
        return mcp_call_forgetful(tool_name, arguments, timeout=timeout)
    if m.get("error"):
        raise RuntimeError(m["error"].get("message", "mcp error"))
    return m["result"]


def state_path(name, session_id=None):
    os.makedirs(HOOK_STATE_DIR, exist_ok=True)
    suffix = ("-" + session_id) if session_id else ""
    safe = (name + suffix).replace("/", "_")
    return os.path.join(HOOK_STATE_DIR, safe + ".json")


def load_state(name, session_id=None, default=None):
    try:
        with open(state_path(name, session_id)) as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_state(name, data, session_id=None):
    with open(state_path(name, session_id), "w") as f:
        json.dump(data, f, ensure_ascii=False)


def extract_text(result):
    """forgetful 返回的 content 数组拼文本。"""
    content = (result or {}).get("content")
    if isinstance(content, list):
        return "\n".join(
            c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"
        )
    return ""


def emit_context(text):
    """UserPromptSubmit/SessionStart:stdout 即注入上下文。"""
    if text:
        print(text)
    sys.exit(0)
