# Worktree 会话预检

会话开始时或涉及 git commit/push/rebase/merge 操作前，运行此检查确认工作环境正确。

## 触发条件

- 用户运行 `/worktree-check`
- 涉及 git commit/push/rebase/merge 操作前自动触发
- 用户提到"检查环境"、"确认分支"、"当前状态"时

## 执行步骤

1. `git rev-parse --show-toplevel` — 确认仓库根目录
2. `git branch --show-current` — 确认当前分支
3. `git status --short` — 查看未提交变更
4. `git log --oneline -3` — 查看最近提交
5. 如果当前分支不是 worktree 分支（即当前在 main/master），发出警告

## 输出格式

```
📂 仓库: <toplevel>
🌿 分支: <branch>
📝 未提交: <count> files
📍 最近: <last 3 commits oneline>
⚠️ 状态: <OK / 警告信息>
```

## 警告规则

- 当前在 `main` 或 `dev` 分支 → ⚠️ "禁止在 main/dev 直接开发，请切换到 worktree"
- 当前在 `master` 分支 → 🚫 "master 已废弃，立即切换"
- `git status` 有未提交变更且用户要执行 rebase/merge → ⚠️ "有未提交变更，建议先 stash"
