#!/usr/bin/env python3
"""git-guard v2 for Claude Code — 复刻 pi extension git-guard.ts v2。

用法(由 settings.json hooks 调起,事件名从 stdin JSON 读):
  git_guard.py prompt     UserPromptSubmit  → L1: 全部 worktree 状态行 stdout 注入
  git_guard.py pretool    PreToolUse(Bash)  → L2 指纹突变 deny + L3 危险命令前缀注入
                            + checkout -b 从远程引用建分支自动补 --no-track
  git_guard.py posttool   PostToolUse(Bash) → L4 危险命令执行后探测残留 → additionalContext

状态(跨会话,等价 pi 的 globalThis):~/.cache/agent-hooks/git-guard.json
  {repo_path: {"fp": 指纹, "line": 上次状态行}}
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_stdin_json, load_state, save_state

GIT_OPS = [
    "rebase-merge", "rebase-apply", "MERGE_HEAD", "sequencer/todo",
    "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG",
]
DANGER_RE = re.compile(
    r"git +(commit[^|;&]*--amend|reset +--hard|push|rebase|cherry-pick|merge"
    r"|checkout|switch|restore|stash +(drop|pop|clear)|clean +-[^ ]*f)"
)
BRANCH_CREATE_RE = re.compile(
    r"^(\s*git +(?:checkout +-b|-B|switch +-c|-C) +\S+ +)(\S+/\S+)(.*)$"
)


def sh(cmd, cwd=None):
    try:
        return subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except Exception:
        return ""


def norm(p):
    try:
        return os.path.realpath(p)
    except Exception:
        return p


def discover_repos(cwd):
    """cwd 所在仓 + 其全部 worktree(realpath 归一去重)。"""
    root = sh("git rev-parse --show-toplevel", cwd=cwd)
    if not root:
        return []
    repos = {norm(root)}
    out = sh("git worktree list --porcelain", cwd=root)
    for line in out.split("\n"):
        if line.startswith("worktree "):
            repos.add(norm(line.split(" ", 1)[1]))
    return sorted(repos)


def repo_status(repo):
    br = sh("git branch --show-current", cwd=repo)
    hd = sh("git rev-parse --short HEAD", cwd=repo)
    if not hd:
        return None, None
    dirty = len([l for l in sh("git status --porcelain", cwd=repo).split("\n") if l.strip()])
    seqs = [f for f in GIT_OPS if os.path.exists(os.path.join(repo, ".git", f))]
    # worktree 的 .git 是文件,序列文件在 gitdir 里
    if os.path.isfile(os.path.join(repo, ".git")):
        try:
            with open(os.path.join(repo, ".git")) as f:
                m = re.search(r"gitdir: (.+)", f.read())
            if m:
                gd = m.group(1).strip()
                seqs += [f for f in GIT_OPS if os.path.exists(os.path.join(gd, f))]
        except Exception:
            pass
    seqs = sorted(set(seqs))
    name = os.path.basename(repo)
    if not br:
        line = "[git-guard] ⚠ %s DETACHED | HEAD=%s | dirty=%d" % (name, hd, dirty)
    else:
        up = sh("git rev-parse --abbrev-ref --symbolic-full-name @{u}", cwd=repo)
        vs = "no-upstream"
        if up and "fatal" not in up:
            counts = sh('git rev-list --left-right --count %s...HEAD' % up, cwd=repo)
            if counts:
                parts = counts.split()
                vs = "behind %s / ahead %s vs %s" % (parts[0], parts[1], up.split("/")[-1])
        line = "[git-guard] %s branch=%s | HEAD=%s | dirty=%d | %s" % (name, br, hd, dirty, vs)
    if seqs:
        line += " | ⚠SEQ:" + ",".join(seqs)
    fp = "%s@%s|%d|%s" % (br, hd, dirty, ",".join(seqs))
    return fp, line


def all_repos_status(cwd):
    result = []
    for repo in discover_repos(cwd):
        fp, line = repo_status(repo)
        if line:
            result.append((repo, fp, line))
    return result


def cmd_prompt():
    ev = read_stdin_json()
    cwd = ev.get("cwd") or os.getcwd()
    lines = [line for _, _, line in all_repos_status(cwd)]
    if lines:
        print("[git-guard 常驻] 嵌套仓库一律 git -C <绝对路径>;\n" + "\n".join(lines))
    sys.exit(0)


def cmd_pretool():
    ev = read_stdin_json()
    cwd = ev.get("cwd") or os.getcwd()
    cmd = (ev.get("tool_input") or {}).get("command") or ""

    def out(obj):
        print(json.dumps(obj, ensure_ascii=False))
        sys.exit(0)

    if not cmd:
        sys.exit(0)

    # L2:指纹突变检测(用户 IDE 切分支/reset 后 agent 无感)
    state = load_state("git-guard")
    for repo, fp, line in all_repos_status(cwd):
        prev = state.get(repo, {}).get("fp")
        if prev and prev != fp:
            state[repo] = {"fp": fp, "line": line}
            save_state("git-guard", state)
            out({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "[git-guard] git 状态在你上次操作后发生突变,本次调用已拦截。\n%s\n"
                        "请先确认目标分支/仓库无误:重读本仓 git 状态后再执行;若确需继续,重发该命令即可。"
                        % line
                    ),
                }
            })
        state.setdefault(repo, {"fp": fp, "line": line})
    save_state("git-guard", state)

    # git-branch-guard:checkout -b/switch -c 从远程引用建分支 → 补 --no-track
    m = BRANCH_CREATE_RE.match(cmd)
    if m and "/" in m.group(2):
        newcmd = "%s%s --no-track%s" % (m.group(1), m.group(2), m.group(3) or "")
        out({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": {"command": newcmd},
                "permissionDecisionReason": "[git-branch-guard] 已自动补 --no-track,防 upstream 误设导致 push 误推远程主干",
            }
        })

    # L3:危险 git 命令 → 前缀注入状态行
    if DANGER_RE.search(cmd):
        lines = [line for _, _, line in all_repos_status(cwd)]
        prefix = "".join("echo '%s' ; " % l for l in (lines or ["[git-guard]"]))
        out({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": {"command": prefix + cmd},
            }
        })
    sys.exit(0)


def cmd_posttool():
    ev = read_stdin_json()
    cwd = ev.get("cwd") or os.getcwd()
    cmd = (ev.get("tool_input") or {}).get("command") or ""
    if not (cmd and DANGER_RE.search(cmd)):
        sys.exit(0)
    warns = []
    for repo in discover_repos(cwd):
        seqs = []
        gd = os.path.join(repo, ".git")
        if os.path.isfile(gd):
            try:
                with open(gd) as f:
                    m = re.search(r"gitdir: (.+)", f.read())
                gd = m.group(1).strip() if m else gd
            except Exception:
                pass
        seqs = [f for f in GIT_OPS if os.path.exists(os.path.join(gd, f))]
        if seqs:
            warns.append("%s: %s" % (os.path.basename(repo), ",".join(seqs)))
    if warns:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "[git-guard L4] 危险 git 命令执行后检测到进行中的序列操作:\n"
                    + "\n".join(warns)
                    + "\n处置指引:确认意图后 git rebase/cherry-pick --continue 或 --abort;"
                      "收尾前勿开始新的 git 序列操作。"
                ),
            }
        }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    {"prompt": cmd_prompt, "pretool": cmd_pretool, "posttool": cmd_posttool}[
        sys.argv[1] if len(sys.argv) > 1 else "prompt"
    ]()
