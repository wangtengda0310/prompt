# Claude Code hooks 备份（2026-09-30 自工作机迁移）

来源：本机 `~/.claude/hooks/`（pi extension 复刻到 Claude Code hooks 的实战版）。
此处为**脱敏快照**——内网标识已替换为占位符，恢复使用前需回填（见下）。
活版本维护在 `~/.claude/hooks/`，改动流程见 `CLAUDE.md` 维护纪律节。

## 组件

| 文件 | 功能 |
|---|---|
| `git_guard.py` | git 四层防护：L1 状态行常驻注入 / L2 分支突变 deny / L3 危险命令前缀注入 + `checkout -b` 自动补 `--no-track` / L4 序列残留警示 |
| `mem_auto.py` | forgetful 共享记忆自动召回：首轮 / 话题漂移 / 30min 周期 + 时间轴 digest；上下文压缩后注入沉淀提醒 |
| `hooks_maintain.py` | 改动 hooks 目录文件时注入维护 checklist（防改完忘同步） |
| `common.py` | 共享库：stdin JSON 解析 / MCP-over-HTTP 客户端 / 状态文件（其余三个的依赖） |
| `CLAUDE.md` | 维护纪律：三层同步模型（代码→共享目录 / 通用知识→forgetful / 机器事实→机器自己的记忆） |

## 接线

把 hooks 命令合并进 `~/.claude/settings.json` 的 `hooks` 字段（事件 × 脚本参数）：

- `UserPromptSubmit` → `git_guard.py prompt`、`mem_auto.py prompt`
- `PreToolUse` (matcher `Bash|PowerShell`) → `git_guard.py pretool`
- `PostToolUse` (matcher `Bash|PowerShell`) → `git_guard.py posttool`
- `PostToolUse` (matcher `Read|Edit|Write|NotebookEdit`) → `hooks_maintain.py posttool`
- `SessionStart` (matcher `compact|clear|resume`) → `mem_auto.py sessionstart`

命令形态：`python "C:/Users/<你>/.claude/hooks/<脚本>.py" <参数>`（Windows 用 `python` 非 `python3`，路径正斜杠）。

## 恢复占位符（脱敏回填）

| 占位符 | 实际含义 |
|---|---|
| `FORGETFUL_HOST` | forgetful MCP 服务器地址（公司内网，见个人记录） |
| `FORGETFUL_USER` | 服务器 SSH 用户名 |
| `LOCAL_HOSTNAME` | 本机主机名 |

`common.py` 的 `DEFAULT_URL` 与 `hooks_maintain.py` 的 checklist、`CLAUDE.md` 的 scp 目标共三处。
也可不改代码：设环境变量 `FORGETFUL_URL` 覆盖 `common.py` 缺省值。

## Windows 适配要点（Mac/Linux 可跳过）

1. `PreToolUse`/`PostToolUse` matcher 必须 `Bash|PowerShell`——启用 PowerShell 工具的机器只写 `Bash` 时防护全旁路
2. `common.py` 已含两修复：三流 `reconfigure(utf-8)`（GBK locale 防乱码）+ `read_stdin_json` 剥 UTF-8 BOM
3. 冒烟测试用 PS 管道前先 `$OutputEncoding = [Text.Encoding]::UTF8`
