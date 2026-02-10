

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
