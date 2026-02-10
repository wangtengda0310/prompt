---
name: image-tools
description: 图像处理工具集 - 包含九宫格图片切分和像素检查功能
author: wangtengda
version: 1.0.0
tags: [image, processing, grid, pixel, analysis]
---

# Image Processing Tools

你有两个强大的图像处理工具可用：图片九宫格切分工具 和 像素检查工具。

## Grid Split - 图片九宫格切分

**可执行文件:** `./bin/gridsplit.exe` (Windows) 或 `./bin/gridsplit` (Linux/Mac)

### 功能说明
将图片按网格切分成多个小图片，支持三种切分模式：
- **equal (等距切分)**: 按指定行列数均匀切分
- **color (颜色检测)**: 根据分割线颜色自动检测网格
- **edge (边缘检测)**: 根据内容边缘自动检测网格

### 常用命令格式

```bash
# 基础用法 - 切分为 3x3 网格
./bin/gridsplit.exe <输入图片> -r 3 -c 3 -o <输出目录>

# 自动检测网格尺寸
./bin/gridsplit.exe <输入图片> --auto -o <输出目录>

# 使用颜色检测模式（例如检测白色分割线）
./bin/gridsplit.exe <输入图片> -m color --line-color "#FFFFFF" -o <输出目录>

# 使用边缘检测模式
./bin/gridsplit.exe <输入图片> -m edge --edge-threshold 50 -o <输出目录>

# 指定输出格式为 JPG
./bin/gridsplit.exe <输入图片> -f jpg -o <输出目录>

# 添加切分边距
./bin/gridsplit.exe <输入图片> --padding 10 -o <输出目录>
```

### 参数说明
- `-r, --rows <行数>`: 行数，0 表示自动检测
- `-c, --cols <列数>`: 列数，0 表示自动检测
- `-m, --mode <模式>`: 切分模式 (equal/color/edge)
- `-o, --output <目录>`: 输出目录
- `--line-color <颜色>`: 分割线颜色，格式 #RRGGBB
- `--color-tolerance <值>`: 颜色容差 (0-255)
- `--edge-threshold <值>`: 边缘阈值 (0-255)
- `-f, --format <格式>`: 输出格式 (png/jpg/jpeg)
- `--padding <像素>`: 切分边距
- `--auto`: 自动检测网格尺寸
- `-v, --verbose`: 详细输出

### 使用场景
当用户请求：
- "把这张图片切成9宫格"
- "将图片按3行4列切分"
- "检测这张图的网格结构"
- "根据白色分割线切分图片"

## Pixel Inspect - 像素检查

**可执行文件:** `./bin/pixelinspect.exe` (Windows) 或 `./bin/pixelinspect` (Linux/Mac)

### 功能说明
检查和分析图片中的像素信息，支持获取指定位置像素的颜色、统计图片颜色分布等。

### 常用命令格式

```bash
# 检查指定位置的像素颜色
./bin/pixelinspect.exe <输入图片> --x 100 --y 200

# 检查多个位置（区域）
./bin/pixelinspect.exe <输入图片> --region 0,0,100,100

# 输出为 JSON 格式
./bin/pixelinspect.exe <输入图片> --x 100 --y 200 --format json

# 获取图片主要颜色统计
./bin/pixelinspect.exe <输入图片> --stats

# 检查像素列表
./bin/pixelinspect.exe <输入图片> --pixels "100,200;150,250;200,300"
```

### 参数说明
- `--x <x坐标>`: 要检查的像素 X 坐标
- `--y <y坐标>`: 要检查的像素 Y 坐标
- `--region <x,y,w,h>`: 检查区域
- `--pixels <列表>`: 像素坐标列表，用分号分隔
- `--stats`: 显示颜色统计信息
- `--format <格式>`: 输出格式 (text/json)
- `--output <文件>`: 输出到文件

### 使用场景
当用户请求：
- "这个位置是什么颜色？"
- "分析这张图的主要颜色"
- "检查图片左上角的像素"
- "获取图片的颜色统计"

## 工作流程指南

### 图片切分流程
1. 确认用户需求和图片位置
2. 根据描述选择合适的切分模式：
   - 规则网格 → `equal` 模式
   - 有分割线 → `color` 模式
   - 不规则内容 → `edge` 模式或 `--auto`
3. 执行切分命令
4. 向用户报告结果和生成的文件

### 像素检查流程
1. 获取图片和要检查的位置
2. 执行像素检查命令
3. 解析并展示颜色信息（RGB值、十六进制颜色代码等）

## 注意事项

1. **路径处理**: Windows 路径包含空格时需要用引号包裹
2. **输出目录**: 确保输出目录存在，工具会自动创建
3. **大图片**: 处理大图片可能需要较长时间
4. **颜色格式**: 十六进制颜色使用 #RRGGBB 格式

## 示例对话

**用户**: "把 test.png 切成 3x3 的九宫格"

**你的回复**:
```
我来帮你将 test.png 切分成 3x3 的网格。

[执行: ./bin/gridsplit.exe test.png -r 3 -c 3 -o output/]

完成！已生成 9 张图片到 output/ 目录：
- test_00.png (左上)
- test_01.png (中上)
- test_02.png (右上)
- test_10.png (左中)
- test_11.png (中心)
- test_12.png (右中)
- test_20.png (左下)
- test_21.png (中下)
- test_22.png (右下)
```

**用户**: "检查这张图片中心位置的颜色"

**你的回复**:
```
我来检查图片中心的颜色。假设图片尺寸为 300x300，中心位置是 (150, 150)。

[执行: ./bin/pixelinspect.exe image.png --x 150 --y 150 --format json]

中心位置 (150, 150) 的颜色：
- RGB: (255, 255, 255)
- 十六进制: #FFFFFF
- 颜色: 白色
```
