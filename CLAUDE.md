使用中文对话
##

## 注意事项
- 需要检查各种软件源是否使用了国内镜像

## 极其重要：代码质量检查
- **永远基于实际文件生成文档**
- 对不确定的信息需要不断追问让我澄清
- 如果存在CLAUDE.md则应使用渐进式披露的方式递归组织目录下所有的文档
- 编写文档时应该引用代码而非复制代码片段

## Git 和版本控制
- 在git仓库修改文件时优先使用git patch给出修改内容并使用git patch命令应用修改内容而非使用Write工具
- 每当完成整个任务并通过回归测试时自提交
- 使用描述性提交消息，捕获更改的完整范围


## 程序开发中 git worktree 的使用
使用git worktree开始新的任务时，在原仓库目录下features.md文件中追加新工作内容的描述，git worktree被移除时，在features.md文件中删除对应描述
可能存在git worktree被移除但features.md文件未被更新的情况，需要自动更新
使用git worktree开始新的任务时，需要切换分支进入worktree对应的工作目录
进入新的worktree工作目录时需要在遵循原有文档更新规则的前提下额外自动更新features.md文件
如何避免worktree两种的开发功能漏提交到git导致丢失

  1. 删除 worktree 前检查未提交更改
  cd {worktreedir}
  git status                    # 检查是否有未提交更改
  git diff --stat               # 查看修改范围
  2. 使用 git worktree remove 而非 rm -rf
  git worktree remove {worktree}# 会警告有未提交更改
  3. 开发完成后先提交再合并
  # 在 worktree 中
  git add .
  git commit -m "feat: "
  git push origin feature/mcp-interface

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
- 代码必须有供code reviewer参考的注释，对外暴露的方法需要有共使用者参考的注释，注释使用中文
- golang程序开发过程优先使用`go run xxx.go`而非`go build && ./xxx` 启动程序
- 需要合理规划任务并利用subagent的并行开发能力
- 需要识别重复的任务，一旦识别到重复的任务需要提醒我整理为agent skills以便ai后续可以基于现有经验快速进行重复工作

### 使用 Context7 查找文档
当请求代码示例、设置或配置步骤，或库/API 文档时，使用 Context7 mcp 服务器获取信息。

### 开发的程序需要有必要的帮助文档
- golang开发的命令行程序需要在help选项中明确指出当前程序的go module名称
- golang程序所在项目的README.md少于100行建议使用go:embeded将其内联并提供一个命令行参数查看文档
- http程序建议有一个/help页面
- CLAUDE.md针对开发者 README.md针对使用者

## 极其重要：Shell 环境和路径处理
@./Shell环境和路径处理.md

## 本地环境
@./本地环境.md

## 工作内容
每天的工作纪要记录在 d:\工作内容-{日期}.md 并依据这些内容为我生成晨会报告和周报，晨会日期是每周一、三、五
