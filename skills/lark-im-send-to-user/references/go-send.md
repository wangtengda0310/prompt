# Go 标准库发送飞书消息参考

零第三方依赖，适合集成到流水线或 Go 项目中。

## 完整代码

```go
package feishu

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// Client 飞书消息客户端
type Client struct {
	AppID     string
	AppSecret string
	token     string
}

// NewClient 创建客户端
func NewClient(appID, appSecret string) *Client {
	return &Client{AppID: appID, AppSecret: appSecret}
}

// SendText 发送文本消息
// receiveID: 接收者 ID（open_id / chat_id / email / user_id / union_id）
// idType: "open_id" | "chat_id" | "email" | "user_id" | "union_id"
func (c *Client) SendText(receiveID, idType, text string) (msgID string, err error) {
	if err := c.ensureToken(); err != nil {
		return "", fmt.Errorf("获取token失败: %w", err)
	}

	content, _ := json.Marshal(map[string]string{"text": text})
	return c.send(receiveID, idType, "text", string(content))
}

// SendPost 发送富文本消息
func (c *Client) SendPost(receiveID, idType, title string, body string) (msgID string, err error) {
	if err := c.ensureToken(); err != nil {
		return "", fmt.Errorf("获取token失败: %w", err)
	}

	postContent := map[string]interface{}{
		"zh_cn": map[string]interface{}{
			"title": title,
			"content": [][]map[string]string{
				{{"tag": "text", "text": body}},
			},
		},
	}
	content, _ := json.Marshal(postContent)
	return c.send(receiveID, idType, "post", string(content))
}

// SendInteractive 发送卡片消息
func (c *Client) SendInteractive(receiveID, idType string, cardJSON string) (msgID string, err error) {
	if err := c.ensureToken(); err != nil {
		return "", fmt.Errorf("获取token失败: %w", err)
	}
	return c.send(receiveID, idType, "interactive", cardJSON)
}

func (c *Client) ensureToken() error {
	if c.token != "" {
		return nil
	}

	body, _ := json.Marshal(map[string]string{
		"app_id":     c.AppID,
		"app_secret": c.AppSecret,
	})
	resp, err := http.Post(
		"https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
		"application/json; charset=utf-8",
		bytes.NewReader(body),
	)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	var result struct {
		Code              int    `json:"code"`
		Msg               string `json:"msg"`
		TenantAccessToken string `json:"tenant_access_token"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return err
	}
	if result.Code != 0 {
		return fmt.Errorf("获取token失败: code=%d, msg=%s", result.Code, result.Msg)
	}

	c.token = result.TenantAccessToken
	return nil
}

func (c *Client) send(receiveID, idType, msgType, content string) (string, error) {
	body, _ := json.Marshal(map[string]string{
		"receive_id": receiveID,
		"msg_type":   msgType,
		"content":    content,
	})

	req, err := http.NewRequest("POST",
		"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type="+idType,
		bytes.NewReader(body),
	)
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json; charset=utf-8")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)

	var result struct {
		Code int    `json:"code"`
		Msg  string `json:"msg"`
		Data struct {
			MessageID string `json:"message_id"`
		} `json:"data"`
	}
	if err := json.Unmarshal(respBody, &result); err != nil {
		return "", fmt.Errorf("解析响应失败: %s", string(respBody))
	}
	if result.Code != 0 {
		return "", fmt.Errorf("发送失败: code=%d, msg=%s", result.Code, result.Msg)
	}

	return result.Data.MessageID, nil
}
```

## 使用示例

```go
client := feishu.NewClient("cli_xxx", "app_secret_xxx")

// 流水线推荐：用邮箱发送（无需提前获取 open_id）
msgID, err := client.SendText("user@company.com", "email", "构建完成")

// 用 open_id 发送
msgID, err := client.SendText("ou_xxx", "open_id", "通知内容")

// 向群发文本
msgID, err := client.SendText("oc_xxx", "chat_id", "配表检查通过")

// 发富文本
msgID, err := client.SendPost("oc_xxx", "chat_id", "构建报告", "详细内容...")

// 发卡片
msgID, err := client.SendInteractive("ou_xxx", "open_id", cardJSON)
```

## 流水线集成

将此代码放入项目中，在 CI 脚本中调用：

```bash
# Docker 镜像中运行
go run ./cmd/notify/main.go \
  --app-id=${FEISHU_APP_ID} \
  --app-secret=${FEISHU_APP_SECRET} \
  --receive-id=${FEISHU_USER_EMAIL} \
  --id-type=email \
  --message="构建完成"
```

## 注意事项

- token 有效期约 2 小时，短任务无需刷新；长运行任务需实现 token 刷新
- bot 发消息需要用户先给 bot 发过消息（建立单聊关系）
- 发送频率限制：个人 5 QPS，群 5 QPS（群内所有 bot 共享）
