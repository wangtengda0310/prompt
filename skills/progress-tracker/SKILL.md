---
name: progress-tracker
description: "开发计划进度持久化。在计划确认后创建 memory 进度文件，每个 Phase 完成后更新进度和角色。当用户说'记录进度'、'更新进度'、'进度如何'、'做到哪了'、'当前状态'时触发。plan-enhanced 完成计划后必须使用此技能创建进度记录。每个 Phase 完成后必须使用 PHASE_DONE 更新进度。与 compact-context-recovery 配合——它读取此技能写入的数据进行恢复。"
---

# 进度管理（Progress Tracker）

> 在开发执行过程中将进度写入 memory 文件，确保 /compact 后可完整恢复。

## 为什么需要这个技能

compact-context-recovery 依赖 memory 中的进度数据来恢复上下文，但如果没有人写入数据，恢复就会失败。本技能负责在开发过程中持续写入进度，是 plan-enhanced（计划）和 compact-context-recovery（恢复）之间的数据桥梁。

## 三种操作

### PHASE_DONE — Phase 完成（最常用）

每个 Phase 完成后**必须**执行：

1. 读取 `memory/active-plan.md`（如不存在则创建）
2. 更新对应 Phase 状态为 `✅ 完成`
3. 记录产出文件列表
4. 更新角色（调度者/执行者）和活跃 agent 列表
5. 更新下一步指向下一个待执行的 Phase
6. 在变更日志追加条目
7. 同时在计划文件验收清单中勾选对应项（`[ ]` → `[x]`）
8. 将更新后的内容写入 `memory/active-plan.md`
9. 确保 `memory/MEMORY.md` 索引中包含 `active-plan.md` 的条目

### PHASE_BLOCKED — Phase 阻塞

遇到无法绕过的问题时执行：

1. 读取 `memory/active-plan.md`
2. 将对应 Phase 状态更新为 `🚫 阻塞({原因})`
3. 在变更日志追加阻塞条目
4. 写入更新后的文件

### PROGRESS_QUERY — 查询进度

用户询问进度时执行：

1. 读取 `memory/active-plan.md`
2. 输出格式化进度报告
3. **不做任何修改**（只读操作）

## 进度文件格式

文件路径：`memory/active-plan.md`

```markdown
---
name: 活跃计划进度
description: 当前会话的计划执行进度，compact 后用于恢复
type: project
---

计划: {计划文件路径} | 共 N 个 Phase | 状态: active
├── Phase 1: {名称} — ✅ 完成
├── Phase 2: {名称} — ⏳ 进行中 (agent: {名})
├── Phase 3: {名称} — 🚫 阻塞 ({原因})
├── Phase 4: {名称} — 🔲 未开始
└── Phase 5: {名称} — 🔲 未开始
角色: 调度者 | 活跃 agent: {列表}
下一步: {具体描述}
变更日志:
- {时间}: {变更描述}
```

状态标记说明：
- `✅ 完成` — Phase 所有步骤完成，测试通过
- `⏳ 进行中 (agent: {名})` — Phase 正在由指定 agent 执行
- `🚫 阻塞 ({原因})` — Phase 无法继续，等待问题解决
- `🔲 未开始` — Phase 尚未启动

## MEMORY.md 索引维护

进度文件创建后，确保 `memory/MEMORY.md` 中包含一行索引：

```
- [活跃计划进度](active-plan.md) — 当前会话的 Phase 执行进度、角色、下一步操作
```

计划完成后，从 MEMORY.md 移除此索引，将 active-plan.md 的状态改为 `completed`。

## 降级策略

如果 memory 目录不可写入：
- 仅在计划文件验收清单中勾选已完成项
- 向用户警告"进度未持久化到 memory"

## 不要做的事

- 不猜测进度 — 不确定时向用户确认后再写入
- 不覆盖变更日志 — 只能追加，不能删除历史条目
- 不在查询时修改进度 — PROGRESS_QUERY 是只读操作
- 不使用 Forgetful MCP — 仅写本地 memory 文件，避免额外依赖
