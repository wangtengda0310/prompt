---
name: plan-enhanced
description: "增强计划模式的质量控制。当进入计划模式（EnterPlanMode）编写实施计划时，或用户要求制定开发计划、实施方案时，必须使用此技能。确保计划自动包含单元测试策略、验收清单、以及多角度审核。即使用户没有明确要求这些内容，计划中也必须包含。适用于所有需要写计划的场景，不论项目大小。"
---

# 增强计划模式

> 在编写实施计划时自动补充质量保障内容，避免计划遗漏测试、验收和审核环节。

## 为什么需要这个技能

用户每次计划确认前都会手动追加：
1. "补充单元测试内容"
2. "补充验收清单"
3. "调用多个 subagent 审核计划"

这些是固定需求，应该在写计划时自动包含，而不是等用户提醒。

## 计划模板

每个实施计划必须包含以下标准章节（无论用户是否要求）：

### 必须包含的章节

#### 1. 实施步骤（核心）
正常写实施步骤，这是计划的主干。

#### 2. 单元测试策略
每个会修改或新增 Go 代码的 Phase，必须追加测试说明：
- 测试文件位置
- 测试函数名称和测试场景
- 使用的 mock/fixture 策略
- 预期覆盖率目标

格式：
```markdown
### Phase N 的测试
- **测试文件**: `xxx_test.go`
- **测试场景**:
  - `TestXxx_正常路径` — 给定合法输入，验证正确输出
  - `TestXxx_边界条件` — 给定空/零值/最大值，验证处理
  - `TestXxx_错误路径` — 给定非法输入，验证错误返回
```

前端 TypeScript 修改的 Phase，补充：
- 组件测试或 E2E 测试的测试场景描述

#### 3. 验收清单
计划末尾必须包含可逐项勾选的验收清单：

```markdown
## 验收清单
- [ ] 功能验收: [具体验收标准1]
- [ ] 功能验收: [具体验收标准2]
- [ ] 单元测试: 所有新增/修改的方法有对应测试
- [ ] 单元测试: `go test ./...` 全部通过
- [ ] 前端类型: 无 TypeScript 编译错误
- [ ] 文档同步: CLAUDE.md / 技能文件已更新
- [ ] 构建验证: `wails3 task build` 成功（如适用）
- [ ] 回归测试: 原有功能未受影响
```

根据实际项目调整验收项。关键是每个验收项必须**具体可验证**，不能写"代码质量好"这种模糊描述。

#### 4. Agent 分工建议
当计划涉及 2 个以上可并行的 Phase 时，必须包含 agent 分工表：

```markdown
## Agent 分工建议
| Agent | 任务 | 预计耗时 | 依赖 |
|-------|------|----------|------|
| backend | Phase 1+2: 后端开发 | 15min | 无 |
| frontend | Phase 3+4: 前端开发 | 20min | backend 完成 |
| docs | Phase 5: 文档更新 | 10min | 无 |
```

### 计划完成后：自动审核

计划写完后、调用 ExitPlanMode 之前，执行以下审核：

#### 自动检查项
1. **测试覆盖** — 每个修改代码的 Phase 都有对应的测试说明
2. **验收清单** — 每个Phase 的产出都有对应的验收项
3. **依赖关系** — Phase 之间的依赖是否正确标注
4. **并行性** — 是否有可以并行但没有标注的 Phase
5. **文档同步** — 是否包含文档/技能更新步骤

#### Subagent 审核（当计划较复杂时）
如果计划涉及 3 个以上 Phase 或修改 5 个以上文件，spawn 1-2 个审核 agent：

```
审核 Agent 1（架构审核）:
- 检查计划中的技术选型是否合理
- 检查 Phase 之间的接口定义是否清晰
- 检查是否遗漏了错误处理策略

审核 Agent 2（完整性审核）:
- 对照需求逐条检查计划是否覆盖
- 检查验收清单是否与计划步骤一一对应
- 检查是否有遗漏的边界情况
```

审核反馈纳入计划后再提交给用户确认。

## 与 task-master 集成（本机已安装）

本机安装了 `task-master` CLI（路径：`C:/Users/v-wangtengda/AppData/Roaming/npm/task-master`），用于结构化的任务分解、依赖管理与进度跟踪。**在符合下述触发条件时，必须使用 task-master 管理计划任务**，而不仅仅是写 Markdown 文件。

### 何时使用 task-master

**必须使用**（满足任一）：
- 计划包含 **≥5 个 Phase** 或 **≥10 个子任务**
- 计划涉及 **多个 agent 并行**，需要明确依赖关系
- 计划周期跨 **多个会话**（需要持久化任务状态）
- 用户明确要求"用 task-master 管理"、"创建 tasks"、"分解任务"

**不需要使用**：
- 单个 Phase 的小型修改（直接写 Markdown 计划即可）
- 探索性、一次性的临时任务
- 仅 1-2 步的简单流程

### task-master 与本技能的协作流程

1. **初始化**（仅项目首次使用）：
   ```bash
   task-master init -y                          # 在项目根创建 .taskmaster/
   task-master models --setup                   # 配置 AI 模型（首次）
   ```

2. **从计划生成任务**：写完计划 Markdown 后，将计划作为 PRD 输入：
   ```bash
   task-master parse-prd --input=<plan.md> --num-tasks=<N>
   ```
   或手工添加：
   ```bash
   task-master add-task --prompt="<Phase 描述>" --priority=high
   ```

3. **分解复杂任务**：
   ```bash
   task-master analyze-complexity --threshold=5     # 找出需要拆分的任务
   task-master expand --id=<id> --num=5             # 拆为子任务
   task-master expand --all                         # 全部展开
   ```

4. **管理依赖**：
   ```bash
   task-master add-dependency --id=<id> --depends-on=<id>
   task-master validate-dependencies                # 检查循环/无效依赖
   ```

5. **执行中跟踪**：
   ```bash
   task-master next                                 # 查询下一个可执行任务
   task-master show <id>                            # 查看任务详情
   task-master set-status <id> in-progress          # 开始
   task-master set-status <id> done                 # 完成
   task-master list -w                              # watch 模式跟踪进度
   ```

6. **会话恢复**（compact 后或新会话）：
   ```bash
   task-master list                                 # 查看所有任务状态
   task-master next                                 # 找到下一步
   ```

### task-master 与 progress-tracker 的分工

| 工具 | 职责 |
|------|------|
| **task-master** | 结构化任务树、依赖图、状态机、AI 辅助分解 |
| **progress-tracker (memory/active-plan.md)** | 调度者身份、变更日志、当前角色、跨会话恢复上下文 |

两者并存：task-master 管"做什么"和"做到哪了"，active-plan.md 管"我是谁、我在干嘛、刚才发生了什么"。

### 使用约束

- **API Key**：task-master 的 AI 功能（parse-prd / expand / research）需要 `ANTHROPIC_API_KEY` 等环境变量，未配置时只能用纯手动命令（add-task / set-status / list）
- **项目本地化**：tasks.json 存储在项目根 `.taskmaster/tasks/`，不污染全局
- **tag 隔离**：用 `task-master tags add <feature-name> --from-branch` 为每个 worktree/feature 创建独立任务上下文，避免任务混淆
- **失败回退**：task-master 命令失败时（如未 init、无 API key），降级为只写 active-plan.md，不阻塞计划制定

## 执行纪律

### 写计划时
1. 先收集需求和技术背景
2. 按模板写计划（实施步骤 + 测试策略 + 验收清单 + Agent 分工）
3. **判断是否启用 task-master**（见上节"何时使用"）；如启用，将 Phase 同步为 task-master 任务
4. 自动检查清单
5. 复杂计划 spawn 审核 agent
6. 综合审核结果修改计划与任务
7. 调用 ExitPlanMode 提交给用户

### 计划确认后（必须执行）
- 立即使用 progress-tracker 技能创建 `memory/active-plan.md` 进度文件
- 写入完整的 Phase 列表和初始状态（全部 🔲 未开始）
- 确保 `memory/MEMORY.md` 索引中包含 active-plan.md 条目
- **如启用 task-master**：执行 `task-master parse-prd --input=memory/active-plan.md` 或逐个 `add-task` 同步任务；用 `tags add` 为本次计划建立独立 tag

### 计划执行中（每个 Phase 完成后必须执行）
1. 在计划文件验收清单中勾选已完成项（Edit 工具将 `[ ]` 改为 `[x]`）
2. 使用 progress-tracker 技能的 PHASE_DONE 操作更新 `memory/active-plan.md`
3. **如启用 task-master**：`task-master set-status <id> done`，再 `task-master next` 决定下一步
4. 遇到阻塞时使用 PHASE_BLOCKED；在 task-master 中 `set-status <id> review` 或追加 dependency
5. 遇到计划外发现时，先 `update-task` / `add-task` 同步任务，再继续执行

### 计划执行完
- 逐项检查验收清单
- 将 active-plan.md 状态改为 completed
- 从 MEMORY.md 索引中移除 active-plan.md 条目
- **如启用 task-master**：确认 `task-master list` 全部为 done；归档 tag（`tags rename` 加 `-archived` 后缀）
