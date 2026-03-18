

\## Claude Code 官方文档指引



本文档配置基于 Claude Code 官方文档的最佳实践。

官方文档：https://code.claude.com/docs/en/best-practices



\### 官方最佳实践核心原则



1\. \*\*上下文管理\*\*：上下文窗口是最重要的资源，需要积极管理

2\. \*\*验证工作\*\*：为 Claude 提供验证其工作的方法（测试、linter、截图对比）

3\. \*\*先探索，后计划，再编码\*\*：使用 Plan Mode 分离探索和执行

4\. \*\*提供具体上下文\*\*：引用特定文件、提到约束条件、指向示例模式

5\. \*\*频繁纠正\*\*：使用 Esc 键停止、/clear 重置、/rewind 回退



\### 官方文档资源



\- \[最佳实践](https://code.claude.com/docs/en/best-practices) - 完整的最佳实践指南

\- \[概览](https://code.claude.com/docs/en/overview) - Claude Code 功能和使用场景

\- \[CLI 参考](https://code.claude.com/docs/en/cli-reference) - 命令行完整参考

\- \[扩展 Claude Code](https://code.claude.com/docs/en/extend) - Skills、Hooks、Subagents、MCP



\### CLAUDE.md 编写最佳实践



根据官方文档，有效的 CLAUDE.md 应该：



\*\*应该包含：\*\*

\- Claude 无法猜到的 Bash 命令

\- 与默认值不同的代码风格规则

\- 测试说明和首选的测试运行器

\- 仓库礼仪（分支命名、PR 约定）

\- 项目特定的架构决策

\- 开发环境特性（必需的环境变量）

\- 常见陷阱和非显而易见的行为



\*\*不应该包含：\*\*

\- Claude 可以通过阅读代码弄清楚的任何内容

\- Claude 已经知道的标准语言约定

\- 详细的 API 文档（链接到文档即可）

\- 频繁变化的信息

\- 长篇解释或教程

\- 逐文件的代码库描述

\- "编写干净代码"之类的不言而喻的实践



\*\*关键建议：\*\*

\- 保持简洁。对每一行，问："删除这会导致 Claude 犯错吗？"

\- 像对待代码一样对待 CLAUDE.md：出错时审查，定期修剪

\- 可以通过添加强调（如 "IMPORTANT" 或 "YOU MUST"）来提高遵守度

\- 使用 `@path/to/import` 语法导入其他文件



\### 常见失败模式（官方文档）



1\. \*\*"厨房水槽"会话\*\*：在一个会话中处理多个不相关的任务

&#x20;  - 修复：在不相关的任务之间使用 `/clear`



2\. \*\*反复纠正\*\*：Claude 反复做错，你反复纠正

&#x20;  - 修复：两次失败纠正后，`/clear` 并编写更好的初始提示



3\. \*\*过度指定的 CLAUDE.md\*\*：文件太长，Claude 忽略一半内容

&#x20;  - 修复：无情修剪。如果 Claude 已经正确执行，删除该指令或转换为 hook



4\. \*\*信任-验证差距\*\*：Claude 产生看似合理但不处理边缘情况的实现

&#x20;  - 修复：始终提供验证（测试、脚本、截图）



5\. \*\*无限探索\*\*：要求 Claude "调查"某个东西而不限定范围

&#x20;  - 修复：缩小调查范围或使用 subagents



\### 上下文管理策略



\- 使用 `/clear` 在任务之间重置上下文窗口

\- 使用 `/compact <instructions>` 自定义压缩行为

\- 使用 Esc+Esc 或 `/rewind` 选择消息检查点并选择"从此处总结"

\- 在 CLAUDE.md 中自定义压缩行为，如 `"压缩时，始终保留修改文件的完整列表和任何测试命令"`



\### 会话管理命令



\- `Esc`：停止 Claude 的操作

\- `Esc + Esc` 或 `/rewind`：打开回退菜单

\- `/clear`：在不相关的任务之间重置上下文

\- `/rename`：给会话一个描述性名称

\- `claude --continue`：恢复最近的会话

\- `claude --resume`：从最近的会话中选择





