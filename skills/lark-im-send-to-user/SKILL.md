---
name: lark-im-send-to-user
description: "向飞书指定用户或群发送消息 — 支持交互式使用和流水线/CI场景。当用户说'发飞书消息给XX'、'通知XX'、'在流水线中发飞书通知'、'CI发消息'时触发。支持文本/Markdown/卡片/图片/文件等多种消息类型，支持open_id/姓名/邮箱作为接收者，支持个人消息和群消息。与 lark-im 的区别：本 skill 专注'发送'单一动作，额外覆盖流水线场景（curl/Go HTTP零依赖方案），不依赖 lark-cli 认证。当需要搜索消息、管理群聊、回复消息等非发送操作时用 lark-im。"
---

# lark-im-send-to-user

向飞书指定用户或群发送消息的专用技能。覆盖两种使用场景：
1. **交互式**：在 Claude Code 中日常使用，有 lark-cli 可用
2. **流水线/CI**：在 CI/CD 环境中使用，只有 appId + appSecret，零依赖

## 场景判断

根据使用环境自动选择方案：

| 场景 | 特征 | 推荐方案 |
|------|------|---------|
| Claude Code 日常使用 | 有 lark-cli、已登录 | `lark-cli im +messages-send` |
| CI/CD 流水线 (Linux) | 只有 appId/appSecret | curl + OpenAPI |
| CI/CD 流水线 (Go 项目) | 有 Go 环境 | Go 标准库 HTTP |
| CI/CD 流水线 (Windows) | PowerShell 可用 | PowerShell Invoke-RestMethod |

**判断方式**：
- 如果用户提到"流水线"、"CI"、"pipeline"、"Docker"、"容器"→ 走流水线方案
- 否则 → 走 lark-cli 方案

## 安全约束

发消息是不可逆操作，**发送前必须确认**：
1. 接收者（谁或哪个群）
2. 消息内容
3. 发送身份（bot 或 user）

除非用户明确说"发送"或"确认"，否则不要发送。

## 交互式场景：使用 lark-cli

### 步骤 1：确定接收者

接收者可以是以下任一格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| open_id | `ou_xxx` | 最可靠，直接使用 |
| 姓名 | `张三` | 需先通过 lark-contact 解析 |
| 邮箱 | `xxx@ztgame.com` | 需先通过 lark-contact 解析 |
| chat_id | `oc_xxx` | 群聊，直接使用 |
| 群名 | `配表检查群` | 需先通过 `lark-cli im +chat-search` 搜索 |

**当用户没有提供 open_id 时**，使用 lark-contact 查找：

```bash
# 按姓名搜索
lark-cli contact +search-user --query "张三" --as user --format json

# 按邮箱搜索（query 也支持邮箱）
lark-cli contact +search-user --query "zhangsan@ztgame.com" --as user --format json

# 按群名搜索
lark-cli im +chat-search --query "配表检查" --as bot --format json
```

搜索到多个结果时，列出候选人让用户选择，不要擅自选第一个。

### 步骤 2：选择消息类型

| 需求 | 方式 | 说明 |
|------|------|------|
| 纯文本 | `--text` | 保持原始格式，不转换 |
| 简单富文本 | `--markdown` | 转为飞书 post，有标题/列表/代码块 |
| 精确控制 | `--content` | 直接传 JSON，支持卡片等复杂类型 |
| 图片 | `--image` | 自动上传本地图片或 URL |
| 文件 | `--file` | 自动上传本地文件或 URL |

### 步骤 3：发送

```bash
# 向个人发送纯文本（最常用）
lark-cli im +messages-send --user-id ou_xxx --text "消息内容" --as bot

# 向群发送纯文本
lark-cli im +messages-send --chat-id oc_xxx --text "消息内容" --as bot

# 向个人发送 Markdown
lark-cli im +messages-send --user-id ou_xxx --markdown $'## 标题\n\n- 项目1\n- 项目2'

# 发送卡片消息
lark-cli im +messages-send --chat-id oc_xxx --msg-type interactive --content '{...卡片JSON...}'

# 预览不发送
lark-cli im +messages-send --user-id ou_xxx --text "测试" --dry-run
```

**Bot 限制**：bot 必须已与目标用户有单聊关系（用户曾给 bot 发过消息），否则发送失败。

## 流水线场景

### 凭证准备

所有流水线方案共用两个凭证，在 CI/CD 的 Secret/变量中配置：
- `FEISHU_APP_ID`：应用 ID（`cli_xxx`）
- `FEISHU_APP_SECRET`：应用密钥

核心流程都是两步：
1. `POST /open-apis/auth/v3/tenant_access_token/internal` → 获取 token
2. `POST /open-apis/im/v1/messages?receive_id_type=xxx` → 发送消息

### 接收者 ID 选择（重要）

| receive_id_type | receive_id 示例 | 适用场景 | 是否需要预获取 |
|-----------------|----------------|---------|--------------|
| **`email`** | `user@company.com` | **流水线首选**，公司邮箱通常已知 | **不需要** |
| `open_id` | `ou_xxx` | 交互式场景，最通用 | 需要（lark-contact 或 API 查询） |
| `chat_id` | `oc_xxx` | 向群发消息 | 需要（lark-cli +chat-search） |
| `user_id` | `xxx` | 企业内唯一，跨应用一致 | 需要 `contact:user.employee_id:readonly` scope |
| `union_id` | `xxx` | 开发者维度唯一 | 需要 |

**流水线推荐用 `email`**：员工邮箱通常可以直接从 Git 提交记录、JIRA、企业通讯录中获取，无需提前调用 API 查 open_id。已验证可用。

### 方案 A：curl（Linux/通用 CI，推荐）

最轻量，零依赖。Linux Docker 中运行无编码问题。

```bash
# 1. 获取 tenant_access_token
TOKEN=$(curl -s -X POST \
  'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"${FEISHU_APP_ID}\",\"app_secret\":\"${FEISHU_APP_SECRET}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2a. 用 email 发送（推荐，无需预获取 open_id）
curl -s -X POST \
  'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=email' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "{\"receive_id\":\"user@company.com\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\\":\\\"构建成功\\\"}\"}"

# 2b. 用 open_id 发送（如果已有 open_id）
curl -s -X POST \
  'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "{\"receive_id\":\"ou_xxx\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\\":\\\"消息内容\\\"}\"}"

# 2c. 向群发送
curl -s -X POST \
  'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "{\"receive_id\":\"oc_xxx\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\\":\\\"群通知\\\"}\"}"
```

**Windows Git Bash 中文乱码问题**：Git Bash 默认 GBK 编码会导致中文消息损坏。解决方法：
- 在 Linux Docker 中运行（推荐）
- 或使用下面的 PowerShell/Go 方案

### 方案 B：PowerShell（Windows CI）

```powershell
# 获取 token
$body = '{"app_id":"' + $env:FEISHU_APP_ID + '","app_secret":"' + $env:FEISHU_APP_SECRET + '"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$resp = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -Method POST -ContentType 'application/json; charset=utf-8' -Body $bytes
$token = $resp.tenant_access_token

# 用 email 发送（推荐）
$msgBody = '{"receive_id":"user@company.com","msg_type":"text","content":"{\"text\":\"构建成功\"}"}'
$msgBytes = [System.Text.Encoding]::UTF8.GetBytes($msgBody)
$sendResp = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=email' -Method POST -ContentType 'application/json; charset=utf-8' -Headers @{Authorization="Bearer $token"} -Body $msgBytes
```

### 方案 C：Go 标准库（Go 项目 CI）

零第三方依赖，适合集成到现有 Go 项目中。详见 [Go 发送参考](references/go-send.md)。

支持 `idType` 参数，可直接传 `"email"` 作为 ID 类型：

```go
client := feishu.NewClient(appID, appSecret)

// 用邮箱发送（流水线推荐）
msgID, err := client.SendText("user@company.com", "email", "构建完成")

// 用 open_id 发送
msgID, err := client.SendText("ou_xxx", "open_id", "构建完成")

// 向群发送
msgID, err := client.SendText("oc_xxx", "chat_id", "群通知")
```

### 消息类型参考

所有方案共用相同的 API 参数：

| 参数 | 说明 |
|------|------|
| `receive_id` | 接收者 ID（邮箱 / open_id / chat_id / user_id / union_id） |
| `receive_id_type` | ID 类型：`email`、`open_id`、`chat_id`、`user_id`、`union_id` |
| `msg_type` | 消息类型：`text`、`post`、`interactive`、`image`、`file`、`audio`、`media`、`share_chat`、`share_user`、`sticker` |
| `content` | 消息内容 JSON（需 double encode） |

**content 格式**：

| msg_type | content 示例 |
|----------|-------------|
| text | `{"text":"消息内容"}` |
| post | `{"zh_cn":{"title":"标题","content":[[{"tag":"text","text":"正文"}]]}}` |
| interactive | `{"config":{},"header":{},"elements":[...]}`（卡片 JSON） |
| image | `{"image_key":"img_xxx"}` |
| file | `{"file_key":"file_xxx"}` |
| audio | `{"file_key":"file_xxx"}` |
| media | `{"file_key":"file_xxx","image_key":"img_xxx"}`（视频，image_key 为封面） |
| share_chat | `{"chat_id":"oc_xxx"}` |
| share_user | `{"user_id":"ou_xxx"}` |

**速率限制**：
- 个人消息：5 QPS
- 群消息：5 QPS（群内所有 bot 共享）
- 文本消息上限：150 KB
- 卡片/富文本上限：30 KB

## 错误处理

| 错误码 | 含义 | 解决方法 |
|--------|------|---------|
| 99991400 | receive_id 无效 | 检查 ID 格式和 receive_id_type |
| 99991401 | 权限不足 | 检查 app scope 是否包含 `im:message:send_as_bot` |
| 99991406 | 不在群内 | bot 需要先被加入目标群 |
| 99991663 | 无单聊关系 | 用户需要先给 bot 发过消息 |
| 99991409 | 频率限制 | 降低发送频率 |
