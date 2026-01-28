- 使用中文对话
- ## Git 和版本控制
- 在git仓库修改文件时优先使用git patch给出修改内容
- 每当完成整个任务时自动添加和提交
- 使用描述性提交消息，捕获更改的完整范围
- 编写文档时应该引用代码而非复制代码片段
- ## 极其重要：代码质量检查
- **永远基于实际文件生成文档**
- 对不确定的信息使用占位符
- golang程序开发过程优先使用`go run xxx.go`而非`go build && ./xxx` 启动程序

**在完成任何任务之前始终运行以下命令：**

自动使用 IDE 的内置诊断工具检查 linting 和类型错误：
   - 运行 `mcp__ide__getDiagnostics` 检查所有文件的诊断
   - 在认为任务完成之前修复任何 linting 或类型错误
   - 对你创建或修改的任何文件都这样做

这是在处理任何与代码相关的任务时绝不能跳过的关键步骤。
- ## 使用 Context7 查找文档

当请求代码示例、设置或配置步骤，或库/API 文档时，使用 Context7 mcp 服务器获取信息。
- ## 规则改进触发器

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
---

## Story Flicks 项目配置

### API 密钥配置（backend/.env）
```bash
# 文本生成提供商：DeepSeek
text_provider="deepseek"
deepseek_api_key=sk-dd1f6abb74774be8b0fd69baa203e1be
text_llm_model=deepseek-chat

# 图像/视频生成提供商：Kling AI
image_provider="kling"
kling_api_key=AdmArFgneGE9PhHfbyt9dJPdMtGaJF9y
kling_secret_key=934pCRbRJdmDY8Y9AEFAGrJQ3BgLyJHK

# Kling 配置
kling_version="1.6"
kling_duration=5
kling_aspect_ratio="16:9"
kling_mode="std"
```

### 启动命令
```bash
# 后端
cd D:/work/aiworkflow/story-flicks/backend
python main.py

# 前端
cd D:/work/aiworkflow/story-flicks/frontend
npm run dev
```

### 访问地址
- 前端应用: http://localhost:5173
- 后端 API: http://127.0.0.1:8000
- API 文档: http://127.0.0.1:8000/docs

### 测试参数示例
```json
{
  "story_prompt": "熊猫和狐狸的故事",
  "segments": 10,
  "language": "zh-CN",
  "text_llm_provider": "deepseek",
  "text_llm_model": "deepseek-chat",
  "image_llm_provider": "kling",
  "resolution": "16:9"
}
```

###
使用git worktree开始新的任务时，在features.md文件中追加新工作内容的描述，git worktree被移除时，在features.md文件中删除对应描述
可能存在git worktree被移除但features.md文件未被更新的情况，需要自动更新
使用git worktree开始新的任务时，需要切换分支进入worktree对应的工作目录
进入新的worktree工作目录时需要在遵循原有文档更新规则的前提下额外自动更新features.md文件

### 注意事项
- DeepSeek API 用于文本生成
- Kling API 用于视频生成（异步，需要轮询）
- 视频生成可能需要几分钟时间

java: D:\Users\lvan\.jdks
本机可能安装了wsl 和git bash如果遇到windows下某些命令不兼容或环境变量设置困难可尝试wsl过bash简化操作
本机可能安装了podman desktop，某些情况可以使用docker容器简化操作或环境搭建
本机安装了ipfs
本机安装了wireguard并使用10.0.0.0网络
本机可以使用ssh root@itsnot.fun免密登录，ipfs与本机同在10.0.0.0网络