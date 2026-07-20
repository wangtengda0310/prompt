使用中文对话
##

## 注意事项
- 需要检查各种软件源是否使用了国内镜像

## 极其重要：任务开始强制检查清单

每次接到任务后、执行任何操作前，必须完成以下检查：

1. **工具选择检查**：这是结构性问题吗？（查找符号定义、调用链、架构理解）→ **必须使用 CodeGraph**（见下方 CodeGraph 章节）
2. **工具选择检查**：这是纯文本搜索问题吗？（日志内容、注释、字符串匹配）→ 可使用 Grep
3. **工作模式检查**：需要理解代码如何工作吗？→ 使用 `codegraph_context` 而非 Agent 委托探索
4. **规则回顾检查**：本任务涉及哪个 CLAUDE.md 章节？快速浏览相关规则后再动手

**违反后果**：如果本可用 CodeGraph 却用了 Grep/Agent 探索，属于低效工作方式，必须在发现后立即纠正并记录到 `.learnings/LEARNINGS.md`。

## 极其重要：代码质量检查
- **永远基于实际文件生成文档**
- 对不确定的信息需要不断追问让我澄清
- 如果存在CLAUDE.md则应使用渐进式披露的方式递归组织目录下所有的文档
- 编写文档时应该引用代码而非复制代码片段
- **代码引用格式**：引用代码位置时使用 `[方法名](文件名:行号)` 格式，如 `[AddItems](userItemManager.go:615)`。行号会随代码变动偏移，但方法名相对稳定便于定位
- **JSON/Schema 代码片段展示规范**：文档中展示 JSON 等嵌套数据结构片段时，必须用「带层级骨架」——保留父级路径（外层对象 + 关键兄弟字段）、用 `...` 省略不相关兄弟、聚焦的目标片段详写，让读者一眼看出该片段在完整 JSON 树中的位置。**禁止孤立的子结构片段**（如只写一个 step 对象却不显示它属于哪个数组）。判断标准：读者看了片段能否第一时间定位它在最终 JSON 文件的哪一层；若章节标题/前后文字已明确交代位置则不必强行套骨架，避免过度优化
- 禁止编写欺骗性单元测试
- golang单元测试使用testify/assert库而非t.Logxxx方法
- 遇到与事实不符的情况时需要及时让我澄清，不要依赖错误的假设
- 掌握的信息不足以完成任务时需要及时让我澄清，以免后期反攻
- 使用命令报错并成功纠正后，需要更新记忆文件一面后期重复犯错
- 每次代码修改后都需要修改相关文档，如果还没有建立文档则需要补充
- go文件中包含多余3个结构体，结构体总共方法超过9个测根据结构体拆分，评估是否需要每个结构体一个单独的go文件
- 单个源代码文件中超过5个方法考虑拆分
- excel相关的对话、描述、注释等需要澄清"表"的概念具体只一个excel文件还是excel中的某一个sheet以免混淆。在项目中则需要明确统一概念到文档中
- 对话中我有描述与实时不符或前后矛盾你应该立即指出而不是根据错误的假设开始工作，工作如果有任何缺失的信息可以要求我先进行补充而不是自己尝试发掘。
- 分析问题时启用subagent节省当前会话token
- **分析完整性**：分析项目级产物（如所有 Excel 配表、所有 Go 模块）时，先确认总量（文件数/表数/模块数）再展示结果，不允许把部分结果当全量。生成文档或分析后进行自我审查：实际覆盖数量是否与声称的一致
- **使用绝对路径**修改文件
- **信息验证**：对任何影响操作决策的事实性陈述，必须先验证再陈述：
  - 引用 commit 内容 → 先 `git show <sha>` 验证
  - 引用文件内容 → 先 Read/Grep 读取实际内容
  - 引用命令输出 → 先实际执行命令
  - 声称"已存在"/"不存在" → 先 Glob/Grep 验证

## Git 和版本控制
- 在git仓库修改文件时优先使用git patch给出修改内容并使用git patch命令应用修改内容而非使用Write工具
- 每当完成整个任务并通过回归测试时自提交
- 使用描述性提交消息，捕获更改的完整范围


## 程序开发中 git worktree 的使用
worktree 的完整操作流程参见 `using-git-worktrees` skill（项目 .claude/skills/ 下）。

**项目特有规则**（skill 未覆盖的部分）：
- 使用 git worktree 开始新任务时，在原仓库目录下 features.md 文件中追加工作内容描述
- git worktree 被移除时，自动更新 features.md 文件删除对应描述
- 进入新 worktree 工作目录时，遵循原有文档更新规则并额外更新 features.md

## 规则改进触发器

**在完成任何任务之前始终运行以下命令：**

自动使用 IDE 的内置诊断工具检查 linting 和类型错误：
   - 运行 `mcp__ide__getDiagnostics` 检查所有文件的诊断
   - 在认为任务完成之前修复任何 linting 和类型错误
   - 对你创建或修改的任何文件都这样做

这是在处理任何与代码相关的任务时绝不能跳过的关键步骤。

## 任务完成自我检查

每个任务完成后，必须回答：

1. **工具使用检查**：本次任务中是否本可用 CodeGraph 却用了 Grep/Agent？如果是，记录到 `.learnings/LEARNINGS.md`
2. **规则遵循检查**：是否违反了 CLAUDE.md 中的任何"极其重要"或"禁止"条款？
3. **效率检查**：是否有已知的更好方法（如 skills、记忆、学习记录）可以改进本次工作？

## 程序开发
- 代码必须有供code reviewer参考的注释，对外暴露的方法需要有共使用者参考的注释，注释使用中文
- 修改代码需要同步修改注释
- 超过20行的方法需要补充以流程为视角的注释
- golang程序开发过程优先使用`go run xxx.go`而非`go build && ./xxx` 启动程序
- 每次任务都需要合理规划并利用subagent的并行开发能力
- 每次任务完成后需要识别重复的工作，一旦识别到重复的任务需要提醒我整理为agent skills以便ai后续可以基于现有经验快速进行重复工作


### **开发计划**
- 同步设计、实现相关MCP工具，如党项开发项目未接入任何mcp实现则使用stdio模式实现命令行版本
- 合理规划任务利用subagent的并行能力
- 合理拆分代码便于单元测试，先编写测试用例不实现代码，审核测试用例后开始编写代码。

### 使用 Context7 查找文档
当请求代码示例、设置或配置步骤，或库/API 文档时，使用 Context7 mcp 服务器获取信息。

### 开发的程序需要有必要的帮助文档
- golang开发的命令行程序需要在help选项中明确指出当前程序的go module名称
- golang程序所在项目的README.md少于100行建议使用go:embeded将其内联并提供一个命令行参数查看文档
- http程序建议有一个/help页面
- CLAUDE.md针对开发者 README.md针对使用者

## 操作执行规范

### 执行前三问

每次执行操作前，必须回答：

1. **用户要求做什么？** — 只执行用户明确要求的操作，不联想、不添加额外步骤
2. **我打算用什么方式？** — 如果用户指定了方式（如squash），使用对应的标准方式；如果未指定方式但有多种选择，先确认再执行
3. **预期结果是什么？** — 明确预期结果，用于执行后验证

### 执行后必检

每个关键操作完成后，必须：

1. **验证结果** — 检查实际结果是否符合预期
2. **对比偏差** — 如果不符合，立即停止并告知用户，不自行修正、不继续执行后续步骤
3. **确认完成** — 向用户报告结果，等待确认后再继续

### 禁止

- 用替代方案绕过用户的明确要求（如用户说squash却用reset+commit）
- 执行用户未要求的额外操作（如用户说squash却擅自push）
- 发现结果异常后继续执行后续步骤
- 不确认实现方式就执行有歧义的指令

### 工具调用防死循环

当 Read/Glob/Grep 等只读工具返回以下结果时，**禁止**在未经用户确认的情况下连续重试：

- `Wasted call — file unchanged since your last Read` — 文件已读取过，内容未变
- `File does not exist` — 文件不存在
- 连续多次返回相同结果

**正确处理**：
1. 首次遇到时，使用已缓存的文件内容继续工作
2. 如需重新读取，先检查是否真的需要（如 Edit/Write 后需要验证，用 `git diff` 或 `head`/`tail` 命令替代）
3. 连续 3 次以上相同结果 → 立即停止，向用户报告情况

**典型场景**：修改文件后不需要 Read 验证（Edit/Write 工具会报错如果失败），避免无意义的重复读取。

### Bug 修复验证流程（强制）

修复 bug 后必须按以下顺序验证，只有全部通过才能声称"已修复"：

1. 运行 IDE 诊断工具检查 linting/类型错误
2. 运行项目构建命令确认构建通过
3. 如果有相关单元测试，运行测试
4. 如果无法运行验证，明确告知用户需要手动验证的内容

**禁止**：
- 修复后不验证就声称"已修复"
- 跳过构建直接进入下一步操作
- 引入新 bug 时继续执行而不告知用户

### 修复前根因假设（强制）

实施 bug 修复前，必须先向用户陈述：

1. **根因假设**：基于只读调查，我认为问题出在 ___ 因为 ___
2. **修复方案**：我打算修改 ___ 文件的 ___ 逻辑，预期效果是 ___
3. **影响范围**：这个修改可能影响 ___

**等待用户确认后再动手修改代码。**

**禁止**：
- 不建立根因假设就直接修改代码
- "先改了看看"的试错式修复
- 分析前端代码时实际 bug 在后端（或反之）— 先确认问题所在层再深入

## 调试与调查规范

诊断问题时必须遵循**只读调查优先**原则：

1. **优先使用 CodeGraph 进行结构性调查**（见下方 CodeGraph 章节），仅在搜索字符串内容（日志、注释）时使用 Grep
2. 完整阅读关键文件
3. 解释发现并给出根因假设
4. 提出修复方案及影响范围估计
5. **等待用户明确说"开始修复"后再修改代码**

**禁止**：
- 调查阶段使用 Edit/Write/Bash 修改文件
- 未确认根因就开始修复
- 基于猜测进行深度分析
- **Grep 优先于 CodeGraph** 查找符号定义或调用关系

## 调度者身份与上下文保护

当任务涉及多文件修改、跨前后端开发、或需要并行工作时，你的角色是**调度者**而非执行者：

- **调度者职责**：规划、分配任务给 subagent、审核产出、协调依赖
- **禁止**：亲自逐文件编码消耗主会话上下文
- **例外**：单文件小修改（<20行）可以直接处理
- **subagent prompt 自包含**：派给隔离 subagent 的任务，会话内的概念、背景、文档结构要么写进 prompt，要么指向它能读的文件，不能假设它继承当前上下文（它看不到会话历史）。

这条规则在 compact 后仍然有效。不要因为上下文丢失就从调度者变成执行者。

当系统提示中存在未完成的计划文件时，必须按计划执行，不得自行偏离。如果不确定当前进度，使用 `compact-context-recovery` 技能恢复上下文后再继续。

## 极其重要：Shell 环境和路径处理
@./Shell环境和路径处理.md

## 本地环境
@./本地环境.md

## 工作内容
已配置 work-journal skill 管理工作记录与报告，详见 ~/.claude/skills/work-journal/SKILL.md

## Forgetful 记忆入库约定（跨项目生效）

当用户要求将内容导入 forgetful 时，按以下流程执行：

### 用户指令格式

| 用户指令 | AI 行为 |
|----------|---------|
| `"将 XXX 导入 forgetful"` 或 `"记忆入库: XXX"` | 自动查询相关记忆 → 建议关联 → 等用户确认 |
| `"记忆入库: XXX, 自动关联"` | 自动查询 → 自动关联所有相关记忆，不询问 |
| `"记忆入库: XXX, 不关联"` | 直接导入，不建立关联 |

### 工作流程

1. 用户说 `"记忆入库: WSL 中 Python 编码问题"`
2. AI 执行 `query_memory("WSL Python 编码 GBK UTF-8")`
3. AI 展示找到的相关记忆（标题 + ID）
4. AI 询问："建议关联以上记忆，是否确认？"
5. 用户回复 `"确认"` / `"不关联"` / `"再关联 ID 13"`

### 关键原则

- **用户不需要知道记忆 ID**，只需描述内容主题
- **AI 主动查询关联**，不等待用户指定
- **关联标准**：同一主题不同方面、因果关系、补充关系
- **如果用户明确指定 ID**：直接关联，不再询问

### 记忆系统分工

| 场景 | 存储位置 |
|------|----------|
| 用户偏好、反馈规则 | 本地记忆 (`~/.claude/.../memory/`) |
| 项目架构决策 | 本地记忆（项目目录） |
| 需要语义搜索的知识 | **Forgetful** |
| 跨项目通用知识 | **Forgetful** |
| 代码片段、可复用模板 | **Forgetful Code Artifact** |

<!-- CODEGRAPH_START -->
## CodeGraph（强制优先）

**本章节规则优先级高于默认行为。接到任何涉及代码探索的任务时，必须先阅读本节。**

This project has a CodeGraph MCP server (`codegraph_*` tools) configured. CodeGraph is a tree-sitter-parsed knowledge graph of every symbol, edge, and file. Reads are sub-millisecond and return structural information grep cannot.

### 强制决策流程

```
任务开始
  ↓
是否需要查找符号/理解结构/追踪调用链？
  → 是 → 必须使用 CodeGraph（见下方工具选择表）
  → 否 → 是否搜索字符串内容（日志/注释）？
      → 是 → 可使用 Grep
      → 否 → 使用 Read 读取已知文件
```

**禁止行为（发现后立即纠正并记录到 .learnings/）**：
- 用 Grep 查找符号定义或调用关系
- 用 Agent 委托代码探索任务（CodeGraph 已内置索引）
- 用 `codegraph_search` + `codegraph_node` 链式调用代替 `codegraph_context`

### When to prefer codegraph over native search

Use codegraph for **structural** questions — what calls what, what would break, where is X defined, what is X's signature. Use native grep/read only for **literal text** queries (string contents, comments, log messages) or after you already have a specific file open.

| Question | Tool |
|---|---|
| "Where is X defined?" / "Find symbol named X" | `codegraph_search` |
| "What calls function Y?" | `codegraph_callers` |
| "What does Y call?" | `codegraph_callees` |
| "How does X reach/become Y? / trace the flow from X to Y" | `codegraph_trace` (one call = the whole path, incl. callback/React/JSX dynamic hops) |
| "What would break if I changed Z?" | `codegraph_impact` |
| "Show me Y's signature / source / docstring" | `codegraph_node` |
| "Give me focused context for a task/area" | `codegraph_context` |
| "See several related symbols' source at once" | `codegraph_explore` |
| "What files exist under path/" | `codegraph_files` |
| "Is the index healthy?" | `codegraph_status` |

### Rules of thumb

- **Answer directly — don't delegate exploration.** For "how does X work" / architecture questions, answer with 2-3 codegraph calls: `codegraph_context` first, then ONE `codegraph_explore` for the source of the symbols it surfaces. For a specific **flow** ("how does X reach Y") start with `codegraph_trace` from→to — one call returns the whole path with dynamic hops bridged — then ONE `codegraph_explore` for the bodies; don't rebuild the path with `codegraph_search` + `codegraph_callers`. Codegraph IS the pre-built index, so spawning a separate file-reading sub-task/agent — or running a grep + read loop — repeats work codegraph already did and costs more for the same answer.
- **Trust codegraph results.** They come from a full AST parse. Do NOT re-verify them with grep — that's slower, less accurate, and wastes context.
- **Don't grep first** when looking up a symbol by name. `codegraph_search` is faster and returns kind + location + signature in one call.
- **Don't chain `codegraph_search` + `codegraph_node`** when you just want context — `codegraph_context` is one call.
- **Don't loop `codegraph_node` over many symbols** — one `codegraph_explore` call returns several symbols' source grouped in a single capped call, while each separate node/Read call re-reads the whole context and costs far more.
- **Index lag**: the file watcher debounces ~500ms behind writes; don't re-query immediately after editing a file in the same turn.

### If `.codegraph/` doesn't exist

The MCP server returns "not initialized." Ask the user: *"I notice this project doesn't have CodeGraph initialized. Want me to run `codegraph init -i` to build the index?"*
<!-- CODEGRAPH_END -->
