---
name: self-healing-git
description: 自愈Git工作流自动化 — 维护实时仓库拓扑模型，预测操作安全性，自动恢复常见失败
---

## 触发条件

以下场景触发此skill：
- 涉及worktree、submodule、多分支的复杂git操作
- 用户说"使用自愈git"或"/self-healing-git"
- cherry-pick、rebase、分支迁移等高风险操作

## REPO_STATE 模型

持久化追踪以下信息：

```yaml
worktrees:
  - path: /d/work/xcard-qa-tools/rain-qa-func/.claude/worktrees/xxx
    branch: feature-xxx
    base_branch: main
    created_at: 2026-04-28

submodules:
  - path: rain-robot
    current_commit: abc123
    expected_commit: def456

protected_branches:
  - main
  - dev

pending_operations:
  - type: cherry-pick
    commits: [commit1, commit2]
    status: in_progress
```

## 执行前验证（任何git命令前）

### 1. 仓库上下文验证
```bash
git rev-parse --show-toplevel
git branch --show-current
git worktree list
```

### 2. 操作安全性预测
根据REPO_STATE模型预测：
- 是否会创建孤立提交？
- 是否会覆盖其他worktree？
- 是否会破坏submodule同步？
- 是否违反protected_branch规则？

### 3. 风险评估输出
```
[SAFE] / [WARNING] / [DANGER]
- 预测结果：...
- 建议操作：...
- 回滚方案：...
```

## 自动恢复程序

### 场景1：dev分支缺失
```
1. 搜索所有remote：git branch -a | grep dev
2. 搜索submodule：cd submodule && git branch -a | grep dev
3. 如找到：提示用户确认后checkout
4. 如未找到：创建新dev分支基于main
```

### 场景2：push被拒绝
```
1. 分析diverged history：git log --graph --left-right HEAD...origin/main
2. 评估选项：
   - rebase：适合线性历史，警告冲突风险
   - merge：适合保留历史，警告复杂度
   - force-push：标记[DANGER]，必须用户确认
3. 推荐最优选项并等待确认
```

### 场景3：worktree创建失败
```
1. 检查master/main混淆：git branch -a
2. 如master存在但main不存在：提示分支迁移
3. 如base branch不存在：搜索remote或创建
4. 清理残留目录后重试
```

### 场景4：submodule不同步
```
1. 检测：git submodule status
2. 如不一致：git submodule update --init --recursive
3. 如仍有冲突：标记手动解决
```

## 完整工作流测试

自主执行以下流程验证系统：

```
1. 从最新main创建feature分支
2. 跨2个submodule修改代码
3. 运行测试确认通过
4. squash为干净提交
5. 通过PR-like流程合并到dev
6. 验证无提交丢失（git log --oneline对比）
```

## 禁止

- 不验证REPO_STATE就执行git命令
- 在[DANGER]评估下不确认就继续
- 遇到submodule问题不报告就跳过
