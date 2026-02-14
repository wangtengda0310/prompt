使用中文对话

## Claude Code 官方文档指引

本文档配置基于 Claude Code 官方文档的最佳实践。
官方文档：https://code.claude.com/docs/en/best-practices

### 官方最佳实践核心原则

1. **上下文管理**：上下文窗口是最重要的资源，需要积极管理
2. **验证工作**：为 Claude 提供验证其工作的方法（测试、linter、截图对比）
3. **先探索，后计划，再编码**：使用 Plan Mode 分离探索和执行
4. **提供具体上下文**：引用特定文件、提到约束条件、指向示例模式
5. **频繁纠正**：使用 Esc 键停止、/clear 重置、/rewind 回退

### 官方文档资源

- [最佳实践](https://code.claude.com/docs/en/best-practices) - 完整的最佳实践指南
- [概览](https://code.claude.com/docs/en/overview) - Claude Code 功能和使用场景
- [CLI 参考](https://code.claude.com/docs/en/cli-reference) - 命令行完整参考
- [扩展 Claude Code](https://code.claude.com/docs/en/extend) - Skills、Hooks、Subagents、MCP

### CLAUDE.md 编写最佳实践

根据官方文档，有效的 CLAUDE.md 应该：

**应该包含：**
- Claude 无法猜到的 Bash 命令
- 与默认值不同的代码风格规则
- 测试说明和首选的测试运行器
- 仓库礼仪（分支命名、PR 约定）
- 项目特定的架构决策
- 开发环境特性（必需的环境变量）
- 常见陷阱和非显而易见的行为

**不应该包含：**
- Claude 可以通过阅读代码弄清楚的任何内容
- Claude 已经知道的标准语言约定
- 详细的 API 文档（链接到文档即可）
- 频繁变化的信息
- 长篇解释或教程
- 逐文件的代码库描述
- "编写干净代码"之类的不言而喻的实践

**关键建议：**
- 保持简洁。对每一行，问："删除这会导致 Claude 犯错吗？"
- 像对待代码一样对待 CLAUDE.md：出错时审查，定期修剪
- 可以通过添加强调（如 "IMPORTANT" 或 "YOU MUST"）来提高遵守度
- 使用 `@path/to/import` 语法导入其他文件

### 常见失败模式（官方文档）

1. **"厨房水槽"会话**：在一个会话中处理多个不相关的任务
   - 修复：在不相关的任务之间使用 `/clear`

2. **反复纠正**：Claude 反复做错，你反复纠正
   - 修复：两次失败纠正后，`/clear` 并编写更好的初始提示

3. **过度指定的 CLAUDE.md**：文件太长，Claude 忽略一半内容
   - 修复：无情修剪。如果 Claude 已经正确执行，删除该指令或转换为 hook

4. **信任-验证差距**：Claude 产生看似合理但不处理边缘情况的实现
   - 修复：始终提供验证（测试、脚本、截图）

5. **无限探索**：要求 Claude "调查"某个东西而不限定范围
   - 修复：缩小调查范围或使用 subagents

### 上下文管理策略

- 使用 `/clear` 在任务之间重置上下文窗口
- 使用 `/compact <instructions>` 自定义压缩行为
- 使用 Esc+Esc 或 `/rewind` 选择消息检查点并选择"从此处总结"
- 在 CLAUDE.md 中自定义压缩行为，如 `"压缩时，始终保留修改文件的完整列表和任何测试命令"`

### 会话管理命令

- `Esc`：停止 Claude 的操作
- `Esc + Esc` 或 `/rewind`：打开回退菜单
- `/clear`：在不相关的任务之间重置上下文
- `/rename`：给会话一个描述性名称
- `claude --continue`：恢复最近的会话
- `claude --resume`：从最近的会话中选择

### 注意事项
- 需要检查各种软件源是否使用了国内镜像

### 极其重要：代码质量检查
- **永远基于实际文件生成文档**
- 对不确定的信息需要不断追问让我澄清
- 如果存在CLAUDE.md则应使用渐进式披露的方式递归组织目录下所有的文档

## Git 和版本控制
- 在git仓库修改文件时优先使用git patch给出修改内容并使用git patch命令应用修改内容
- 每当完成整个任务并通过回归测试时自提交
- 使用描述性提交消息，捕获更改的完整范围
- 编写文档时应该引用代码而非复制代码片段

### 程序开发中 git worktree 的使用
使用git worktree开始新的任务时，在features.md文件中追加新工作内容的描述，git worktree被移除时，在features.md文件中删除对应描述
可能存在git worktree被移除但features.md文件未被更新的情况，需要自动更新
使用git worktree开始新的任务时，需要切换分支进入worktree对应的工作目录
进入新的worktree工作目录时需要在遵循原有文档更新规则的前提下额外自动更新features.md文件

## 规则改进触发器

**在完成任何任务之前始终运行以下命令：**

自动使用 IDE 的内置诊断工具检查 linting 和类型错误：
   - 运行 `mcp__ide__getDiagnostics` 检查所有文件的诊断
   - 在认为任务完成之前修复任何 linting 或类型错误
   - 对你创建或修改的任何文件都这样做

这是在处理任何与代码相关的任务时绝不能跳过的关键步骤。

- 现有规则未涵盖的新代码模式
- 跨文件的重复类似实现
- 可以防止的常见错误模式
- 一致使用的新库或工具
- 代码库中新兴的最佳实践

## 分析过程：
- 将新代码与现有规则进行比较
- 识别应该标准化的模式
- 寻找外部文档的引用
- 检查一致的错误处理模式
- 监控测试模式和覆盖率

## 程序开发
- golang程序开发过程优先使用`go run xxx.go`而非`go build && ./xxx` 启动程序

### 使用 Context7 查找文档
当请求代码示例、设置或配置步骤，或库/API 文档时，使用 Context7 mcp 服务器获取信息。

### 开发的程序需要有必要的帮助文档
- golang开发的命令行程序需要在help选项中明确指出当前程序的go module名称
- golang程序的README.md少于100行建议使用go:embeded内联并提供一个命令行参数查看文档
- http程序建议有一个/help页面

## 极其重要：Shell 环境和路径处理
@Shell环境和路径处理.md

## 本地环境
@本地环境.md
