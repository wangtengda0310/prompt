---
name: git-safe
description: 执行 git 操作前强制验证仓库上下文，防止错误的分支推送和文件位置错误
---

## 触发条件

执行任何 git 命令前必须运行此 skill，特别是以下场景：
- git push / pull / fetch
- git merge / rebase
- git commit
- git checkout / switch
- git cherry-pick
- git worktree 相关操作

## 验证步骤（必须按顺序执行）

### 1. 确认仓库根目录
```bash
git rev-parse --show-toplevel
```
- 确认输出路径是否匹配预期操作位置
- 如操作涉及 submodule，确认当前是否在 submodule 目录内

### 2. 确认当前分支
```bash
git branch --show-current
```
- 禁止在 master 分支上操作（master 已废弃）
- 禁止在 main 分支上直接开发
- 禁止在 dev 分支上直接开发

### 3. 确认 worktree 状态（如适用）
```bash
git worktree list
```
- 确认当前目录是否为 worktree
- 确认 worktree 的 base branch 是否正确

### 4. 确认远程分支映射（push 前必须）
```bash
git branch -vv
```
- 确认本地分支追踪的远程分支是否正确
- 确认远程分支名是 main 而非 master

### 5. 确认提交状态（merge/rebase 前必须）
```bash
git log --oneline -5
git status --short
```
- 显示最近 5 条提交
- 显示未暂存/未提交变更的文件数
- 等待用户确认后再继续

## 禁止操作清单

- ❌ 在未验证仓库位置前执行任何 git 命令
- ❌ 在未确认分支名称为 main 前 push 到远程
- ❌ 在 worktree 中对 dev 分支使用 `-f`/`--force` 推送
- ❌ 假设分支存在而不验证
- ❌ 在 submodule 目录执行根仓库的 git 操作

## 错误处理

如果验证结果与预期不符：
1. 立即停止当前操作
2. 向用户报告实际状态（仓库路径、当前分支、worktree 列表）
3. 等待用户明确指示后再继续
