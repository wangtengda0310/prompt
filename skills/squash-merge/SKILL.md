---
name: squash-merge
description: |
  将多个 commit 合并为一个，rebase 到最新 origin/main。
  触发条件
    - 用户说"合并"、"squash"、"准备合并"
    - 用户说"走流程"（指完整的 squash → rebase 流程）
  **不要触发**：
    - 用户只是要 commit（不做 squash）
    - 用户说"push"（只是推送当前分支）
---

## 前置检查（每步必做）

执行任何操作前，先输出当前状态：

```bash
git branch --show-current     # 确认在 worktree 分支
git rev-parse --show-toplevel # 确认仓库路径
git status --short            # 确认无未提交变更
```

**如果当前在 main/dev/master 分支 → 停止，警告用户。**
**如果有未提交变更 → 提示用户先 commit 或 stash。**

## 执行步骤

### Step 1: 确认 squash 范围

```bash
# 查看当前分支相对于 main 的提交数
git fetch origin
git log --oneline origin/main..HEAD
```

向用户展示提交列表，确认 squash 范围。

### Step 2: Squash

```bash
# 找到分支点和 main 的分叉点
MERGE_BASE=$(git merge-base HEAD origin/main)

# 用 heredoc 把合并后的 commit message 写入临时文件（文件优先，避免复杂引号嵌套）
cat > /tmp/squash-msg.txt <<'EOF'
<用户确认的 commit message>
EOF

# 用 rebase -i 把分叉点之后的所有 commit 压缩为一个：
# - GIT_SEQUENCE_EDITOR：todo 编辑器，把第 2 个及之后的 pick 改为 squash（保留第 1 个作为基底）
# - GIT_EDITOR：commit message 编辑器，用上面的临时文件覆盖 git 生成的合并 message 文件
GIT_SEQUENCE_EDITOR="sed -i '2,\$s/^pick/squash/'" \
GIT_EDITOR="cp /tmp/squash-msg.txt" \
git rebase -i $MERGE_BASE
```

**说明**：
- `rebase -i` 默认会打开交互式编辑器，这里通过 `GIT_SEQUENCE_EDITOR`（编辑 todo 列表）和 `GIT_EDITOR`（编辑 commit message）两个环境变量注入非交互指令，实现全自动压缩。
- 若分叉点之后只有 1 个 commit，`sed` 不会改写任何行，rebase 直接完成（无需 squash，原 commit 保留）。
- 中断或出错时用 `git rebase --abort` 回到压缩前状态。

**commit message 规范**：
- 描述对话的主题/目标
- 不描述内部修改过程
- 格式参考：`feat: 添加活动Wiki检查页面` / `fix: 修复武将过滤条件失效` / `refactor: 前端目录结构重组`

### Step 3: Rebase onto main

```bash
git fetch origin
git rebase origin/main
```

**冲突处理**：
1. 冲突 → 向用户报告，等待确认解决方案
2. 冲突解决后 `git rebase --continue`

### Step 4: 推送 worktree 分支

```bash
git push origin <worktree-branch>
```

如果远程已有旧版本（squash 后历史变了），需要 force-push **worktree 分支**（不是 dev/main）：
```bash
git push --force-with-lease origin <worktree-branch>
```

### Step 5: 报告结果

向用户输出：
```
✅ Squash 完成: <count> commits → 1 commit
✅ Rebase 完成: 基于 origin/main (<short-sha>)
📝 Commit: <short-sha> <message>
```

## 错误恢复

| 错误 | 恢复方法 |
|------|---------|
| squash 后发现 commit message 写错 | `git commit --amend -m "新消息"` |
| rebase 冲突无法解决 | `git rebase --abort`，向用户报告 |
| 误操作 reset --hard | `git reflog` 找到之前 HEAD，`git reset --hard <sha>` |
| force-push 了 dev | **立即告知用户**，不要尝试自行恢复 |

## 本技能自进化
遇到以下情形则与用户沟通后对本技能进行迭代：
- 实际执行过程与本技能给出的步骤不一致
- 用户明确要求进行本技能的功能迭代
- 你在工作过程中识别出了用户的明显git提交、合并操作习惯
- claude 的 /insights 功能识别出的用户git操作习惯