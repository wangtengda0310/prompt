---
name: daily-review
description: |
  每日自动回顾分析技能 — 回顾前一天所有会话，分析 Skill 使用质量、开发效率，生成报告并自动优化。

  触发条件（满足任一即触发）：
  - 用户要求回顾昨天或某天的工作效率和 Skill 使用情况
  - 用户询问某个 skill 的使用频率或质量
  - 用户要求生成每日回顾报告
  - 定时任务自动触发（凌晨 3:03）

  不要使用此 skill 的场景：
  - 用户只是记录工作内容（用 work-journal）
  - 用户只是查看 git log（不涉及效率分析）
  - 用户要修改代码、运行测试等非回顾分析任务
---

# 每日自动回顾分析

## 文件位置约定

| 类型 | 路径模板 | 示例 |
|------|----------|------|
| 每日回顾报告 | `d:\work\报告\每日回顾-{YYYY-MM-DD}.md` | `d:\work\报告\每日回顾-2026-04-01.md` |
| 分析缓存 | `~/.claude/skills/daily-review/cache/{date}.json` | 缓存原始分析数据 |
| 趋势数据 | `~/.claude/skills/daily-review/trends.json` | 累积的趋势指标 |
| 学习记录 | `~/.claude/.learnings/LEARNINGS.md` | 自动追加的经验条目 |

如果 `d:\work\报告\` 目录不存在，自动创建。
如果 `~/.claude/skills/daily-review/cache/` 目录不存在，自动创建。

## 核心流程

### 步骤 1：运行分析脚本

```bash
python ~/.claude/skills/daily-review/scripts/daily-review.py --date {YYYY-MM-DD}
```

脚本功能：
- 从 `~/.claude/history.jsonl` 提取目标日期的会话数据
- 统计会话数、Token 消耗、轮次、涉及项目
- 提取 Skill 调用记录（匹配 `/skill-name` 模式）
- 输出结构化 JSON 到缓存文件

**参数说明**：
- `--date`：目标日期，默认为昨天（YYYY-MM-DD）
- `--from / --to`：日期范围，用于周回顾
- `--output`：输出路径，默认缓存目录

**如果脚本不存在或执行失败**，使用以下手动分析流程：
1. 运行 `python ~/.claude/skills/work-journal/scripts/history-summary.py --date {date}` 获取会话列表
2. 在主仓库和各子模块执行 `git log --since="{date} 00:00:00" --until="{date} 23:59:59" --all --oneline` 获取提交记录
3. 读取当天的纪要文件 `d:\work\工作内容-{date}.md`（如存在）

### 步骤 2：深度分析（Claude 语义判断）

基于步骤 1 的数据，进行以下分析：

#### 2.1 Skill 触发质量评估

对每个被调用的 Skill，判断：
- **触发准确性**：是否在正确的场景被触发，是否有误触发或漏触发
- **执行完整性**：Skill 是否完整执行了定义的流程
- **结果有效性**：Skill 输出是否对用户有价值

评估等级：正常 / 低频（可能遗忘）/ 异常（触发不当）

#### 2.2 效率指标计算

| 指标 | 计算方式 |
|------|----------|
| 输入输出比 | 总输入 Token / 总输出 Token |
| 提交占比 | 包含 git commit 的会话数 / 总会话数 |
| 平均轮次 | 总对话轮次 / 会话数 |
| Skill 利用率 | 涉及 Skill 调用的会话数 / 总会话数 |
| 最耗 Token 会话 | Token 消耗最高的会话及原因分析 |

#### 2.3 重复工作模式识别

检测以下重复模式：
- 多次执行相同或相似的命令序列
- 反复修复同类错误
- 在不同项目中重复相同的配置步骤
- 可以自动化但未自动化的操作

### 步骤 3：生成报告

将分析结果按下方"报告模板"格式写入 `d:\work\报告\每日回顾-{日期}.md`。

写入规则：
- 报告中的数值必须来自实际数据，不得编造
- 对比昨日数据从 `trends.json` 中读取，首次运行时标记为 "首日（无对比）"
- 如果某项数据无法获取，标记为 "N/A" 并说明原因
- 报告生成后，将当日关键指标追加到 `trends.json`

### 步骤 4：自动优化

根据分析结果执行以下优化操作：

#### 4.1 追加学习记录

在 `~/.claude/.learnings/LEARNINGS.md` 中追加发现的经验条目：

```markdown
### {YYYY-MM-DD} 发现

- **{模式类型}**: {具体描述}
  - 影响: {对效率的影响}
  - 建议: {改进方案}
```

#### 4.2 Skill Description 优化建议

如果发现 Skill 触发异常（误触发或漏触发），生成该 Skill 的 description 修改建议，
格式为：

```
Skill: {skill-name}
当前 description 问题: {问题描述}
建议修改: {新的 description 片段}
```

将建议写入报告的"改进建议"章节，不直接修改 SKILL.md（需要用户确认）。

#### 4.3 新 Skill 建议

如果发现重复工作模式且无现有 Skill 覆盖，建议创建新 Skill：

```
建议新 Skill: {skill-name}
覆盖场景: {描述}
预期收益: {效率提升估算}
```

## 报告模板

```markdown
# 每日回顾 {YYYY-MM-DD}

## 概览

| 指标 | 数值 | 对比昨日 |
|------|------|----------|
| 会话总数 | {TOTAL_SESSIONS} | {SESSION_DIFF} |
| 活跃项目 | {ACTIVE_PROJECTS} | -- |
| 总 Token 消耗 | {TOTAL_TOKENS} | {TOKEN_DIFF%} |
| Skill 调用次数 | {SKILL_CALL_COUNT} | {SKILL_DIFF} |
| 平均会话轮次 | {AVG_TURNS} | {TURNS_DIFF} |

## 项目分布

| 项目 | 会话数 | Token 消耗 | 主要工作 |
|------|--------|-----------|----------|
| {PROJECT_NAME} | {N} | {N} | {简述} |

## Skill 使用统计

### 按频率排序

| Skill | 调用次数 | 涉及会话 | 评估 |
|-------|---------|----------|------|
| {SKILL_NAME} | {N} | {SESSION_IDS} | {正常/低频/异常} |

### 触发质量详情

{对每个异常或低频 Skill 的具体分析}

## 效率指标

- **总输入 Token**: {INPUT_TOKENS}
- **总输出 Token**: {OUTPUT_TOKENS}
- **输入输出比**: {RATIO}
- **最耗 Token 会话**: {SESSION_ID} ({TOKENS} tokens) — {原因简述}
- **包含 git commit 的会话占比**: {RATIO}

## 发现的问题

### 错误模式

{列出当天反复出现的错误或失败模式}

### 重复工作

{列出可以自动化但被手动重复执行的操作}

## 改进建议

### Skill 优化建议

{针对已有 Skill 的触发条件或执行流程的优化建议}

### 新 Skill 建议

{针对重复工作模式建议的新 Skill}

### 流程优化

{其他流程层面的改进建议}

## 自动执行的优化

- [ ] 已追加的 .learnings 条目: {条目标题}
- [ ] trends.json 已更新
- [ ] 报告已归档至 {路径}

---
*本报告由 daily-review skill 自动生成于 {GENERATED_AT}*
```

## 定时任务配置

### Cron 配置

使用 `CronCreate` 创建每日定时任务：

```
CronCreate({
  cron: "3 3 * * *",
  prompt: "执行每日回顾：运行 /daily-review 分析昨天的工作效率和 Skill 使用情况，生成报告。",
  recurring: true,
  durable: true
})
```

- 触发时间：每天凌晨 3:03（避开整点高峰）
- durable: true，确保重启后任务仍有效
- recurring 任务 7 天自动过期，需要在报告中提醒续期

### 自注册续期机制

每次定时任务执行时，检查任务的剩余有效期：
1. 调用 `CronList` 查看当前所有 cron 任务
2. 如果 daily-review 任务不存在（过期被删除），重新 `CronCreate` 创建
3. 在报告末尾记录续期状态

```markdown
## 定时任务状态

- 任务状态: {运行中/已过期需重新注册}
- 上次续期: {日期}
- 预计过期: {日期（创建日+7天）}
```

### 首次部署

首次使用此 Skill 时，执行以下初始化：
1. 确认 `d:\work\报告\` 目录存在
2. 确认 `~/.claude/skills/daily-review/cache/` 目录存在
3. 初始化 `trends.json`（空数组 `[]`）
4. 创建 `~/.claude/.learnings/LEARNINGS.md`（如不存在）
5. 创建 CronCreate 定时任务

## 通用规则

1. **不直接读大文件**：`history.jsonl` 可能超过 1000 行，必须通过脚本过滤后再使用，避免 token 膨胀
2. **报告去重**：生成报告前检查 `d:\work\报告\每日回顾-{日期}.md` 是否已存在，存在则询问用户是否覆盖
3. **日期格式**：所有日期使用 `YYYY-MM-DD` 格式，默认分析昨天
4. **trends 追加**：每次报告生成后，将关键指标追加到 `trends.json`，保留最近 30 天数据
5. **数据真实性**：报告中的数值必须来自实际统计，无法获取时标记 N/A 并说明原因
6. **分析脚本不存在时的降级方案**：使用 history-summary.py + git log 手动分析，不阻塞报告生成
