# hooks 维护纪律（本目录 = Claude Code hook 脚本）

> 本文件在项目树外，**不会自动进上下文**——靠 `hooks_maintain.py`（PostToolUse）在触碰本目录文件时注入指引。此处是详细版。

## 三层同步模型（改完 hook 的收尾流程）

| 层 | 载体 | 什么时候更新 |
|---|---|---|
| 代码 | `FORGETFUL_HOST:~/forgetful-share/claude-code-share/`（唯一权威源） | 本机改动冒烟过后 **scp 回写**，其他机器从此拉取 |
| 通用知识 | forgetful **#466**（部署入口+修复史）/ **#465**（API 映射表） | 通用缺陷、新 hook 事件映射、部署方式变化 |
| 机器事实 | forgetful **#467**（本机 LOCAL_HOSTNAME 记录） | 本机特有配置/环境变化 |

- **分工**：共享包 `CHANGELOG.md` 记「改了什么」，forgetful 记「为什么/坑在哪」
- forgetful 更新遵循 #455 纪律：update 原条目、勿建平行条目、结论推翻走 obsolete

## 本机已装组件（2026-09-30）

`git_guard.py`（L1-L4 + branch-guard）+ `mem_auto.py`（召回/漂移/压缩沉淀）+ `common.py`（MCP 客户端，依赖）+ `hooks_maintain.py`（本提醒机制）。
**未装**：mem_guard / file_watch / context_files / jnpm_context（在共享包，要装直接拷 + 按 snippet 接线）。

## Windows 适配要点（详见 forgetful #467）

1. settings 命令用 `python`（非 python3，Store 别名坑）+ 正斜杠绝对路径
2. PreToolUse/PostToolUse matcher 必须 `Bash|PowerShell`（只写 Bash 时 PowerShell 工具全旁路）
3. common.py 已带两修复：三流 reconfigure(utf-8) + read_stdin_json 剥 BOM（Mac 侧空操作）

## 冒烟测试坑（PS 5.1 实测）

- 管道喂 JSON 前必须 `$OutputEncoding = [Text.Encoding]::UTF8`（默认 ASCII，中文变 `?`）
- 管道会带**双 UTF-8 BOM**（`read_stdin_json` 已剥离，但自写测试代码要防）
- 改 hook 状态文件（`~/.cache/agent-hooks/*.json`）一律用 python 自己 load/save——PS `Set-Content -Encoding utf8` 带 BOM 炸 `json.load`
- L4 测试的 scratch 仓记得 `git init`（只建 `.git/` 子目录不算 git 仓，discover_repos 静默返回空）

## 状态文件

`~/.cache/agent-hooks/`（跨 hook 进程共享，等价 pi 的 globalThis）：`git-guard.json`（指纹基线）、`mem-auto-<session>.json`、`mcp-session.json`（MCP 会话缓存，404 自动重建）
