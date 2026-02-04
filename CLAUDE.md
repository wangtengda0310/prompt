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

### 开发的程序需要有必要的帮助文档
- golang开发的命令行程序需要在help选项中明确指出当前程序的go module名称
- golang程序的README.md少于100行建议使用go:embeded内联并提供一个命令行参数查看文档
- http程序建议有一个/help页面

### 注意事项
- DeepSeek API 用于文本生成
- Kling API 用于视频生成（异步，需要轮询）
- 视频生成可能需要几分钟时间
- 需要检查各种软件源是否使用了国内镜像

java: D:\Users\lvan\.jdks
本机可能安装了wsl 和git bash如果遇到windows下某些命令不兼容或环境变量设置困难可尝试wsl过bash简化操作
本机可能安装了podman desktop，某些情况可以使用docker容器简化操作或环境搭建
本机安装了ipfs
本机安装了wireguard并使用10.0.0.0网络
本机可以使用ssh root@itsnot.fun免密登录，ipfs与本机同在10.0.0.0网络

---

## 极其重要：Shell 环境和路径处理

### 问题描述
本机同时存在 **Git Bash**、**PowerShell**、**WSL** 三种 shell 环境，混用会导致严重的路径和语法错误。

### 环境对照表

| 环境 | 路径格式 | 使用场景 | 限制 |
|------|----------|----------|------|
| **PowerShell** | `D:\work\...` | SSH 远程命令、文件传输 | 不支持 `<` 重定向 |
| **WSL** | `/mnt/d/work/...` | Linux 环境、Docker 操作 | 需要 `wsl -d` 前缀 |
| **Git Bash** | `D:/work/...` | Git 操作 | 路径转换不可靠 |

### ⚠️ 禁止的操作模式

```powershell
# ❌ 禁止：PowerShell 中使用 Bash 风格重定向
ssh root@server 'mysql ...' < schema.sql

# ❌ 禁止：混用 Windows 路径和 WSL 命令
wsl -d CentOS -- php D:\work\file.php

# ❌ 禁止：复杂的嵌套引号（转义会失败）
ssh server "echo '$VAR' | grep '$PATTERN'"

# ❌ 禁止：在旧版 PowerShell 中使用 &&
cmd1 && cmd2
```

### ✅ 正确的操作模式

```powershell
# ✅ SSH 远程命令：使用 PowerShell
ssh root@itsnot.fun 'podman ps'

# ✅ 文件传输：先上传，再在远程执行
scp local.sql root@itsnot.fun:/tmp/
ssh root@itsnot.fun 'mysql ... < /tmp/local.sql'

# ✅ WSL 操作：明确指定环境
wsl -d CentOS9-stream -- bash -c 'cd /mnt/d/work && php script.php'

# ✅ 多步骤命令：分开执行或使用 ;
ssh root@itsnot.fun 'cmd1; cmd2'
```

### 必须遵循的原则

1. **明确环境**：每次命令前确定使用哪个 shell
2. **避免嵌套**：复杂操作分解为多步
3. **文件优先**：用文件代替管道和重定向
4. **测试先做**：复杂命令先简单测试语法

### 常见修复模板

```powershell
# 场景1：需要通过管道处理远程输出
# ❌ 错误
ssh server 'cat file' | grep pattern

# ✅ 正确
ssh server 'cat /tmp/file.txt' > output.txt
# 然后本地处理

# 场景2：在 WSL 中使用 Windows 文件
# ❌ 错误
wsl -- php D:/work/file.php

# ✅ 正确
wsl -d CentOS -- php /mnt/d/work/file.php

# 场景3：向远程服务导入 SQL
# ❌ 错误
ssh server 'mysql db' < schema.sql

# ✅ 正确
scp schema.sql root@server:/tmp/
ssh root@server 'mysql db < /tmp/schema.sql'
```

### 调试检查清单

当命令失败时，按此顺序检查：
1. 是否混用了不同环境的语法？
2. 路径格式是否与当前 shell 匹配？
3. 是否使用了不支持的重定向（PowerShell 的 `<`）？
4. 引号转义是否正确？
## 终端与命令执行规则（必须遵守）

### 当前环境
- **默认终端**: Git Bash (`/usr/bin/bash`)
- **路径格式**: Unix 风格 (`/c/Users/...`, `/d/work/...`)

### 命令执行前必须检查

在执行任何 Bash 命令前，必须先判断：

1. **是 Windows 特定命令吗？**
   - `Get-ChildItem`, `New-NetFirewallRule`, `Get-Process` 等
   - → 使用: `powershell.exe -Command "命令"`

2. **包含 Windows 路径吗？**
   - `C:\...`, `D:\...`, `%LOCALAPPDATA%`
   - → 使用: `powershell.exe -Command "命令"`
   - → 或转换为 Unix 路径: `/c/...`, `/d/...`

3. **是 Git 或 Linux 命令吗？**
   - `git`, `ssh`, `grep`, `cat`, `ls`
   - → 直接使用 Bash 工具
   - **必须**转换 Windows 路径为 Unix 格式

4. **是 SSH 远程命令吗？**
   - → 使用 Bash，注意避免复杂引号嵌套
   - 管道和重定向优先用文件传递

4. **是 WSL 命令吗？**
   - 注意某些程序在windows环境中配置了windows路径导致wsl中无法使用，例如claude code的/ide命令
   - 注意当前回话是在windows中启动还是在wsl中启动，如果是wsl中启动则不需要wsl -d

### 路径转换表（必须应用）
| Windows 格式 | Unix 格式 |
|--------------|-----------|
| `C:\Users\lvan` | `/c/Users/lvan` |
| `D:\work\...` | `/d/work/...` |
| `C:\Program Files\...` | `/c/Program Files/...` |
| `$LOCALAPPDATA` | `/c/Users/lvan/AppData/Local` |

### 禁止的行为
- ❌ 在 Bash 中直接使用 `C:\...` 路径
- ❌ 在 Bash 中使用 `&&` 连接命令（Git Bash 不支持）
- ❌ 复杂的嵌套引号（转义会失败）
- ❌ 同一个命令失败后盲目重试 3 次以上
