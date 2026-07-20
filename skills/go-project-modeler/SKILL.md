---
name: go-project-modeler
description: Use when analyzing Go project structure, visualizing module dependencies, understanding code architecture, or preparing low-token project context for AI subagents.
---

# Go 项目建模器

## 触发条件
- 当前目录包含 `go.mod` 文件
- 用户请求分析 Go 项目结构
- subagent 需要获取项目上下文

## 五大能力速查

| 能力 | 说明 | 参数 |
|------|------|------|
| 模块架构图 | 包依赖关系、模块分层 | `-v architecture` |
| 类型关系图 | struct 组合关系 | `-v types` |
| 接口实现导航 | 正向 + 逆向映射 | `-v interfaces` |
| 调用流/数据流图 | 函数调用链、数据流向 | `-v callflow` |
| 代码健康度 | 多维度量化评估 | `-v health` |

## 快速调用示例

### 人类使用
```bash
/go-model                                    # HTML5 全景报告
/go-model -s rain-excel-checker             # 限定模块范围
/go-model -v health -f html                  # 单个能力
/go-model -v architecture -f mermaid         # 导出图表
```

### subagent 使用
```bash
/go-model -f summary -s <scope>              # 快速概况
/go-model -f json -v interfaces -s <scope>   # 接口详情
```

## 参数速查表

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--fmt` | `-f` | `auto` | 输出格式：html/mermaid/json/summary |
| `--scope` | `-s` | `.` | 分析范围（模块/包路径） |
| `--view` | `-v` | `all` | 单个视图：architecture/types/interfaces/callflow/health |
| `--width` | `-w` | `auto` | ASCII 宽度计算器：cjk-2x/wcwidth/custom |
| `--output` | `-o` | `-` | 输出路径（`-` 表示标准输出） |

## 格式选择规则

| 调用场景 | 默认格式 | 说明 |
|---------|---------|------|
| 人类直接调用 | `html` | 人类默认获取交互页面 |
| subagent 调用 | `summary` | Skill 模板中硬编码 |
| `--fmt=auto` | 按场景自动判断 | 不依赖 LLM 自行判断 |

**Token 预算参考**：
- Summary：~20% 原始数据
- JSON：~60% 原始数据
- HTML5/Mermaid：~100% 原始数据

## subagent 委派规则

**核心原则**：禁止在主会话中执行分析工作（summary 格式除外）。

| 场景 | 策略 |
|------|------|
| 单能力请求 | 1 个 subagent |
| 全景 HTML 报告 | 并行 N 个 subagent + 主会话合并 |
| subagent 主动调用 | 直接返回 summary，≤150 字 |
| summary 格式 | 可在主会话直接执行 |

### Token 节省效果
| 场景 | 主会话直接执行 | subagent 委派 |
|------|--------------|-------------|
| 单能力 summary | ~500 token | ~100 token |
| 接口导航 JSON | ~5000 token | ~500 token |
| 全景 HTML 报告 | ~20000 token | ~300 token（文件路径） |

## 前置条件检查

执行前自动检测：
1. 当前目录是否存在 `go.mod`
2. `go list ./...` 是否成功
3. 可选工具是否安装

**必需工具**：`go list`, `go mod graph`, `go vet`
**可选工具**：`goplantuml`, `goda`, `gocognit`

## 边界条件处理

| 场景 | 处理方式 |
|------|---------|
| 空 Go 项目 | 返回"项目无可分析文件" summary |
| 编译错误项目 | 降级为 `grep` + `find` 文本提取 |
| 巨型项目（1000+ 文件） | `--scope` 必填，按模块分片 |
| 多模块项目 | 支持 `--scope` 指定子模块 |
| CGO 项目 | CGO 模块跳过 |
| 生成代码（*.pb.go） | 默认排除 |

## 渐进式文档结构

**Layer 0: SKILL.md（本文件）** — 每次必加载
- 触发条件、能力速查表、调用示例
- 格式选择规则、subagent 委派规则摘要

**Layer 1: docs/*.md** — 按需加载
- [架构图](docs/architecture-diagram.md) — 模块依赖关系
- [类型关系图](docs/type-relationship.md) — struct 组合/embedding
- [接口导航](docs/interface-navigation.md) — 正向/逆向接口映射
- [调用流](docs/call-flow.md) — 函数调用链、数据流
- [健康度](docs/health-metrics.md) — 多维度量化评估

**Layer 2: docs/ref/*.md** — 极少使用
- 健康度公式、输出模板、提取工具细节

## 健康度分级

| ChaosIndex | 等级 | 颜色 | 行动建议 |
|-----------|------|------|---------|
| 0-20 | 健康 | 绿色 | 保持 |
| 21-40 | 关注 | 黄色 | 监控 |
| 41-60 | 混乱 | 橙色 | 重构 |
| 61-100 | 失控 | 红色 | 紧急 |

## 相关技能

- [subagent-driven-development](../subagent-driven-development/) — subagent 委派模式
- [渐进式披露](../progressive-disclosure/) — 文档组织原则
