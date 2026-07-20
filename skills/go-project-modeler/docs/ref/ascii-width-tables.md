# ASCII 宽度查找表

## 概述

本文档提供完整的 Unicode 字符宽度查找表，用于 ASCII 图的右边框对齐计算。

## Unicode EastAsianWidth 标准

### 宽度分类

| 分类 | 说明 | 宽度 |
|------|------|------|
| **A** (Ambiguous) | 宽度取决于上下文 | 1 或 2 |
| **F** (Fullwidth) | 全角字符 | 2 |
| **H** (Halfwidth) | 半角字符 | 1 |
| **N** (Neutral) | 中性字符 | 1 |
| **Na** (Narrow) | 窄字符 | 1 |
| **W** (Wide) | 宽字符 | 2 |

## CJK 字符范围

### 中文（简体/繁体）
```
U+4E00 - U+9FFF  : CJK 统一汉字
U+3400 - U+4DBF  : CJK 扩展A
U+20000 - U+2A6DF: CJK 扩展B
U+2A700 - U+2B73F: CJK 扩展C
U+2B740 - U+2B81F: CJK 扩展D
U+2B820 - U+2CEAF: CJK 扩展E
U+2CEB0 - U+2EBEF: CJK 扩展F
```
**宽度**：2

### 日文假名
```
U+3040 - U+309F  : 平假名
U+30A0 - U+30FF  : 片假名
```
**宽度**：2

### 韩文
```
U+1100 - U+11FF  : 韩文 Jamo
U+AC00 - U+D7AF  : 韩文音节
```
**宽度**：2

## 标点符号

### 中文标点
```
U+3001 ： 、
U+3002 ： 。
U+FF01 - FF0F ： ！＂＃＄％＆＇（）＊＋，－．／
U+FF1A - FF20 ： ：；＜＝＞？＠
U+FF3B - FF40 ： ［＼］＾＿｀
U+FF5B - FF65 ： ｛｜｝～
```
**宽度**：2

### 英文标点
```
U+0021 - U+002F : ! " # $ % & ' ( ) * + , - . /
U+003A - U+0040 : : ; < = > ? @
U+005B - U+0060 : [ \ ] ^ _ `
U+007B - U+007E : { | } ~
```
**宽度**：1

## 数字和字母

### 半角数字
```
U+0030 - U+0039 : 0-9
```
**宽度**：1

### 全角数字
```
U+FF10 - U+FF19 : ０-９
```
**宽度**：2

### 半角字母
```
U+0041 - U+005A : A-Z
U+0061 - U+007A : a-z
```
**宽度**：1

### 全角字母
```
U+FF21 - U+FF3A : Ａ-Ｚ
U+FF41 - U+FF5A : ａ-ｚ
```
**宽度**：2

## Emoji 表情

### 常用 Emoji 范围
```
U+1F300 - U+1F5FF : 符号和象形文字
U+1F600 - U+1F64F : 表情符号
U+1F680 - U+1F6FF : 交通和地图符号
U+2600 - U+26FF  : 杂项符号
U+2700 - U+27BF  : 装饰符号
U+FE00 - U+FE0F  : 变异选择器
```
**宽度**：2（大多数情况）

**注意**：某些 Emoji 是由多个 Unicode 码位组成的序列：
```
👨‍👩‍👧‍👦 = U+1F468 U+200D U+1F469 U+200D U+1F467 U+200D U+1F466
```

## 特殊字符

### 制表符和空格
```
U+0009 : \t (Tab)       → 4 或 8（取决于设置）
U+0020 : 空格           → 1
U+00A0 : 不换行空格     → 1
U+3000 : 全角空格       → 2
```

### 零宽字符
```
U+200B : 零宽空格       → 0
U+200C : 零宽非连接符   → 0
U+200D : 零宽连接符     → 0
U+FEFF : 零宽不换行空格 → 0
```

## Python 实现示例

```python
import unicodedata

def get_char_width(char, calculator='cjk-2x'):
    if calculator == 'en':
        return 1

    if calculator == 'cjk-2x':
        # CJK 范围检查
        if '\u4e00' <= char <= '\u9fff':  # CJK 统一汉字
            return 2
        if '\u3040' <= char <= '\u30ff':  # 日文假名
            return 2
        if '\uac00' <= char <= '\ud7af':  # 韩文
            return 2
        if '\u3001' <= char <= '\u303f':  # CJK 标点
            return 2
        if '\uff01' <= char <= '\uff65':  # 全角符号
            return 2
        return 1

    elif calculator == 'wcwidth':
        # 使用 wcwidth 库
        import wcwidth
        return wcwidth.wcwidth(char)

    elif calculator == 'custom':
        # 用户自定义映射
        return CUSTOM_WIDTH_MAP.get(char, 1)

def calculate_text_width(text, calculator='cjk-2x'):
    return sum(get_char_width(c, calculator) for c in text)
```

## Go 实现示例

```go
package width

import "unicode"

// CJK 范围检查
func isCJK(r rune) bool {
    return (r >= 0x4E00 && r <= 0x9FFF) || // CJK 统一汉字
        (r >= 0x3400 && r <= 0x4DBF) || // 扩展A
        (r >= 0x3040 && r <= 0x30FF) || // 日文假名
        (r >= 0xAC00 && r <= 0xD7AF) // 韩文
}

func isFullwidthPunct(r rune) bool {
    return (r >= 0x3001 && r <= 0x303F) || // CJK 标点
        (r >= 0xFF01 && r <= 0xFF65) // 全角符号
}

// GetCharWidth 返回字符宽度
func GetCharWidth(r rune, calculator string) int {
    if calculator == "en" {
        return 1
    }

    if calculator == "cjk-2x" {
        if isCJK(r) || isFullwidthPunct(r) {
            return 2
        }
        return 1
    }

    if calculator == "wcwidth" {
        // 使用 golang.org/x/text/width
        // ...
    }

    return 1
}

// CalculateWidth 计算文本总宽度
func CalculateWidth(s string, calculator string) int {
    width := 0
    for _, r := range s {
        width += GetCharWidth(r, calculator)
    }
    return width
}
```

## 测试用例

```python
# 测试用例
test_cases = [
    ("中文", 4),           # 2 * 2 = 4
    ("ABC", 3),            # 3 * 1 = 3
    ("混合ABC", 7),        # 2*2 + 3*1 = 7
    ("！", 2),             # 全角感叹号
    ("!", 1),              # 半角感叹号
    ("123", 3),            # 半角数字
    ("１２３", 6),          # 全角数字
    ("🔥", 2),             # Emoji
]

for text, expected in test_cases:
    actual = calculate_text_width(text, 'cjk-2x')
    assert actual == expected, f"{text}: expected {expected}, got {actual}"
```

## 相关文档

- [ASCII 中文宽度](../ascii-width.md) — 使用指南
- [输出模板](output-templates.md) — ASCII 图表模板
