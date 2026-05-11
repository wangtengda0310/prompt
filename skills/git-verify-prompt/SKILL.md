---
name: git-verify-prompt
description: 会话开始时快速验证git上下文，防止错误的分支推送和仓库位置错误
---

## 触发条件

会话涉及任何git操作时，在开始时运行此skill。

## 执行步骤

1. 运行验证命令：
```bash
git rev-parse --show-toplevel && git branch --show-current && git worktree list
```

2. 向用户确认：
   - 仓库位置是否正确（根仓库 vs submodule）
   - 当前分支是否符合预期
   - 是否为worktree（如果是，base branch是否正确）

3. 如需push，额外验证：
```bash
git branch -vv
```

4. 如需merge/rebase，额外验证：
```bash
git log --oneline -5 && git status --short
```

## 快捷用法

用户可以直接说"git验证"或"/git-verify-prompt"触发此skill。
