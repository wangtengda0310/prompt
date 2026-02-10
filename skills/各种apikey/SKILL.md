

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

- DeepSeek API 用于文本生成
- Kling API 用于视频生成（异步，需要轮询）
- 视频生成可能需要几分钟时间