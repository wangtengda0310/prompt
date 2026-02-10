---
name: video-extractor
description: 视频首尾帧提取工具 - 从视频中提取开头和结尾的帧图片
author: lvan
version: 1.0.0
tags: [video, frame, extraction, ffmpeg, processing]
---

# Video Frame Extractor

你可以使用视频首尾帧提取工具从视频文件中提取开头和结尾的帧图片。

## 功能说明

**可执行文件:** `./bin/video-extractor.exe` (Windows) 或 `./bin/video-extractor` (Linux/Mac)

该工具使用 ffmpeg 从视频中提取：
- **首帧**: 从视频开头提取指定数量的帧
- **尾帧**: 从视频结尾提取指定数量的帧

### 常用命令格式

```bash
# 基础用法 - 提取首尾各 1 帧
./bin/video-extractor.exe -input <视频文件路径>

# 指定输出目录
./bin/video-extractor.exe -input <视频文件路径> -output "./frames"

# 提取首尾各 N 帧
./bin/video-extractor.exe -input <视频文件路径> -count 3

# 完整参数示例
./bin/video-extractor.exe -input "video.mp4" -output "./output" -count 2
```

### 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-input` | 输入视频文件路径 (必填) | - |
| `-output` | 输出目录 | `./output` |
| `-count` | 提取首尾各多少帧 | `1` |

### 输出文件命名
```
output/
├── first_frame_1.jpg   # 第1帧
├── first_frame_2.jpg   # 第2帧
├── ...
├── last_frame_1.jpg    # 倒数第1帧
├── last_frame_2.jpg    # 倒数第2帧
└── ...
```

### 使用场景
当用户请求：
- "提取这个视频的首尾帧"
- "把视频的第一帧和最后一帧保存成图片"
- "获取视频开头和结尾的截图"
- "提取视频前3帧和后3帧"

## 工作流程

1. 确认视频文件路径和提取需求
2. 根据需要确定提取的帧数
3. 执行提取命令
4. 向用户报告结果和生成的文件

## 注意事项

1. **依赖要求**: 需要系统安装 ffmpeg 并添加到 PATH
2. **路径处理**: Windows 路径包含空格时需要用引号包裹
3. **输出目录**: 工具会自动创建输出目录
4. **支持格式**: 支持所有 ffmpeg 支持的视频格式 (mp4, avi, mkv, mov 等)
5. **输出格式**: 图片格式为 JPG，质量参数 `-q:v 2`

## 示例对话

**用户**: "提取 video.mp4 的首尾帧"

**你的回复**:
```
我来帮你提取 video.mp4 的首尾帧。

[执行: ./bin/video-extractor.exe -input "video.mp4"]

完成！已保存首尾帧到 ./output 目录：
- first_frame_1.jpg (首帧)
- last_frame_1.jpg (尾帧)
```

**用户**: "把这个视频的前3帧和后3帧都提取出来"

**你的回复**:
```
我来提取视频的前3帧和后3帧。

[执行: ./bin/video-extractor.exe -input "video.mp4" -count 3]

完成！已保存6帧图片到 ./output 目录：
- first_frame_1.jpg, first_frame_2.jpg, first_frame_3.jpg
- last_frame_1.jpg, last_frame_2.jpg, last_frame_3.jpg
```
