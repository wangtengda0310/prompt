# 系统通知脚本 - Claude Stop Hook
# 使用 .NET NotifyIcon 弹出系统托盘气泡通知，可绕过 Windows 免打扰模式

param(
    [string]$Title = "Claude Code",
    [string]$Message = "会话已结束"
)

# 加载必要的 .NET 程序集
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 创建 NotifyIcon 实例
$icon = New-Object System.Windows.Forms.NotifyIcon

# 使用系统信息图标
$icon.Icon = [System.Drawing.SystemIcons]::Information
$icon.BalloonTipTitle = $Title
$icon.BalloonTipText = $Message
$icon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$icon.Visible = $true

# 显示气泡通知（3秒）
$icon.ShowBalloonTip(3000)

# 等待通知显示完成后清理
Start-Sleep -Milliseconds 3500
$icon.Dispose()
