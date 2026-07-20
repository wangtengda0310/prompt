# Learnings

## [LRN-20260520-001] correction

**Logged**: 2026-05-20T15:30:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
在 worktree 中修改文件时，误操作修改了主仓库目录下的同名文件，导致提交落到了错误的分支上。

### Details
当前在 `rain-qa-func/.claude/worktrees/stophook/` worktree 中工作，需要修改 `.claude/settings.json`。由于使用了主仓库的绝对路径 `D:/work/xcard-qa-tools/rain-qa-func/.claude/settings.json`，修改实际落到了主仓库的 `dev` 分支，而非 worktree 的 `worktree-stophook` 分支。

错误路径：`D:/work/xcard-qa-tools/rain-qa-func/.claude/settings.json`（主仓库）
正确路径：`D:/work/xcard-qa-tools/rain-qa-func/.claude/worktrees/stophook/.claude/settings.json`（worktree）

### Suggested Action
1. 修改文件前确认当前工作目录是否在 worktree 中
2. 使用相对路径或 worktree 的绝对路径，避免引用主仓库路径
3. 修改后执行 `git status` 验证变更落在正确的分支

### Metadata
- Source: user_feedback
- Related Files: .claude/settings.json
- Tags: worktree, git, path
- Pattern-Key: worktree.path_confusion
- Recurrence-Count: 1
- First-Seen: 2026-05-20
- Last-Seen: 2026-05-20

### Resolution
- **Resolved**: 2026-05-20T15:35:00+08:00
- **Commit/PR**: 09f2c7d
- **Notes**: 撤销主仓库的误提交（git reset --soft HEAD~1 + git checkout HEAD -- file），重新在 worktree 中修改并提交

---

## [LRN-20260520-002] knowledge_gap

**Logged**: 2026-05-20T15:40:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
PowerShell 脚本包含中文时，如果文件是 UTF-8 无 BOM 编码，执行会报错（中文被截断）。

### Details
创建 `windows-notification.ps1` 脚本时，使用 Write 工具写入中文内容，默认生成 UTF-8 无 BOM 文件。PowerShell 默认以 GBK 编码读取脚本，导致中文参数默认值 `"会话已结束"` 被截断为 `"会话已结`（缺少半个字符），解析失败。

错误信息：
```
����λ�� ... �ַ�: 24
+     [string]$Message = "会话已结�?
+                        ~~~~~~~~~
�ַ���ȱ����ֹ��: "��
```

### Suggested Action
1. PowerShell 脚本含中文时，必须添加 UTF-8 BOM 头
2. 或使用 `-Encoding UTF8` 参数执行（但脚本内部中文仍可能有问题）
3. 优先使用纯英文的 PowerShell 脚本，避免编码问题

### Metadata
- Source: error
- Related Files: ~/.claude/skills/self-improvement/scripts/windows-notification.ps1
- Tags: powershell, encoding, utf8, bom, chinese
- Pattern-Key: powershell.utf8_bom
- Recurrence-Count: 1
- First-Seen: 2026-05-20
- Last-Seen: 2026-05-20

### Resolution
- **Resolved**: 2026-05-20T15:45:00+08:00
- **Notes**: 使用 Python 为文件添加 UTF-8 BOM（`codecs.BOM_UTF8`），脚本可正常执行

---
