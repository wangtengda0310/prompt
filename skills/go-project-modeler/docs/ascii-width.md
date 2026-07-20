# ASCII 中文宽度计算

## 概述

ASCII 图使用中文标识时，需要正确计算字符宽度以确保右边框对齐。本模块提供四档宽度计算器和自动探测机制。

## 核心原则：场景区分

ASCII 图有三种展示场景，宽度可控性完全不同：

| 场景 | 宽度可控 | 能否探测 | 策略 |
|------|---------|---------|------|
| **终端（会话展示）** | 不可控，取决于终端字体 | 能（用户可交互） | 自动探测 + 用户反馈 |
| **文件输出**（.txt/.md） | 不可控，取决于查看工具 | 不能（文件发出后无法交互） | 默认 `cjk-2x`，不探测 |
| **HTML5 中的文本** | **可控**（CSS font-family） | 不需要 | CSS `monospace` 保证 CJK=2 半角，或直接用 SVG |

**关键洞察**：HTML5 模式不需要 ASCII 宽度计算——直接用 SVG/Canvas 渲染关系图，不存在字符宽度问题。ASCII 图在 HTML5 中仅作为无 JS 环境的降级回退。

## 四档宽度计算器

| 计算器 | 规则 | 适用环境 |
|--------|------|---------|
| `cjk-2x` | CJK 字符 = 2 半角宽度 | Windows Terminal / iTerm2 / 大多数等宽终端 |
| `wcwidth` | Unicode EastAsianWidth 标准表 | 严格按标准，覆盖全字符集 |
| `custom` | 用户提供宽度映射表 | 特殊字体 / 非标准终端 |
| `en` | 仅英文，无宽度问题 | 保底模式 |

`auto` 为默认值。

## 自动探测流程（仅终端场景）

**触发条件**：仅在人类直接调用 + 输出包含 ASCII + 配置为 `auto` 时触发。

### 探测步骤

1. 生成测试图案（包含中英文混合的框图）
2. 询问用户"右边框对齐了吗？"
3. 对齐 → 保存当前计算器到配置
4. 不对齐 → 尝试不同宽度系数（1.5x, 2x, 逐字符测量）
5. 找到正确值 → 保存配置
6. 多次尝试失败 → 自动降级为 `en` 英文保底模式

### 不触发探测的场景

- subagent 调用 → 直接使用 `cjk-2x` 默认值
- `--fmt=json` 或 `--fmt=summary` → 不生成 ASCII，跳过宽度计算
- `--fmt=html` → 用 SVG 渲染，不需要 ASCII
- 生成文件（.txt/.md）→ 用 `cjk-2x` 默认值

## 配置方式

### .claude/settings.json
```json
{
  "asciiWidthCalculator": "auto",
  "asciiWidthDefault": "cjk-2x",
  "customWidthMap": {
    "CJK_BASE": 2,
    "FULLWIDTH_PUNCTUATION": 2,
    "EMOJI": 2
  }
}
```

### 参数说明
- `asciiWidthCalculator`：计算器选择
- `asciiWidthDefault`：无头模式（subagent/文件输出）的默认值，默认 `cjk-2x`
- 单次覆盖：`/go-model --width=cjk-2x`

## 宽度查找表

完整的 Unicode 宽度查找表定义在 [Layer 2 文档](ref/ascii-width-tables.md)，包括：
- CJK 统一汉字
- 全角标点符号
- 半角/全角数字
- Emoji 表情

## Skill 内嵌 AI 适配指导

当 auto 检测失败时，Skill 指导 AI 在新环境中执行：
1. 生成探测图案 → 用户反馈
2. 尝试宽度系数
3. 保存配置
4. 或降级英文

## 调用示例

```bash
# 自动探测（终端）
/go-model -f mermaid --width=auto

# 指定计算器
/go-model -f mermaid --width=wcwidth

# 文件输出（使用默认 cjk-2x）
/go-model -f mermaid -o output.txt

# 保底英文模式
/go-model -f mermaid --width=en
```

## 测试图案示例

```
┌──────────────────────┐
│ 中文测试             │
│ ABC Test 123         │
│ 混合文字 Mixed Text  │
└──────────────────────┘
```

如果右边框对齐，说明宽度计算正确。

## 相关文档

- [ASCII 宽度查找表](ref/ascii-width-tables.md) — 完整 Unicode 宽度表
- [输出模板](ref/output-templates.md) — ASCII 图表模板
