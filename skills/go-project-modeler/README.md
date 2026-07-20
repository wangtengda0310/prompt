# go-project-modeler

一个 Claude Code Skill，用图形化方式展示 Go 项目结构，支持人类阅读和 AI agent 通信两种场景。

## 核心价值

- **人类**：直观理解项目架构、定位问题区域
- **AI agent**：低 token 成本获取项目上下文，subagent 间传递结构化数据

## 五大能力

| 能力 | 说明 | 输出 |
|------|------|------|
| 模块架构图 | 包依赖关系、模块分层、目录结构 | 依赖图 |
| 类型关系图 | struct 组合关系、embedding 层级 | 关系图 |
| 接口实现导航 | 正向（interface→struct）+ 逆向（struct→interface） | 导航树 |
| 调用流/数据流图 | 函数调用链、数据流向、模块间交互 | 流程图 |
| 代码健康度/噪声度 | 6 维度量化评估混乱程度 | 雷达图 + 热力图 |

## 四种输出格式

| 格式 | Token 占比 | 场景 |
|------|-----------|------|
| HTML5 交互页面 | — | 人类深度探索，可缩放/拖拽/搜索/折叠 |
| Mermaid + ASCII | 100% | 人类阅读，文档嵌入，终端展示 |
| JSON 结构化 | ~60% | subagent 间传递上下文 |
| Summary 摘要 | ~20% | 快速判断是否需要详情 |
| Bencode | ~40%（待实测） | 极致压缩实验，与 JSON 对比 |

## 快速开始

### 调用 Skill

```bash
# HTML5 全景报告（默认）
/go-model

# 限定模块范围（大型项目必备）
/go-model -s rain-excel-checker

# 单个能力
/go-model -v health -f html

# 导出 Markdown 图表
/go-model -v architecture -f mermaid -o docs/arch.md
```

### 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--fmt` | `-f` | `auto` | 输出格式：html/mermaid/json/summary/bencode |
| `--scope` | `-s` | `.` | 分析范围（模块/包路径） |
| `--view` | `-v` | `all` | 单个视图：architecture/types/interfaces/callflow/health |
| `--width` | `-w` | `auto` | ASCII 宽度计算器：cjk-2x/wcwidth/custom/en |
| `--output` | `-o` | `-` | 输出路径 |

## 项目结构

```
skills/go-project-modeler/
├── SKILL.md                           Layer 0: 入口 (~150行)
├── README.md                          本文件
├── scripts/
│   ├── run-extract.sh                 统一入口：调用 Go 工具链 + 组装 JSON
│   ├── check-deps.sh                  前置条件检查（go.mod、工具可用性）
│   └── calc-health.sh                 健康度指标计算（基于提取的 JSON）
├── templates/
│   ├── html5-report.html              HTML5 报告模板
│   ├── mermaid-*.md                   Mermaid 图表模板
│   └── ascii-*.txt                    ASCII 图表模板
├── docs/
│   ├── architecture-diagram.md        Layer 1: 能力文档
│   ├── type-relationship.md
│   ├── interface-navigation.md
│   ├── call-flow.md
│   ├── health-metrics.md
│   └── ascii-width.md                 输出基础设施文档
└── docs/ref/
    ├── health-formulas.md             Layer 2: 线性扣分函数定义
    ├── output-templates.md
    ├── bencode-spec.md                Bencode 编码规范
    ├── extractor-details.md           Go 工具链调用细节
    └── ascii-width-tables.md          Unicode 宽度查找表
```

## 前置条件

### 必需工具
- Go 1.16+（`go list`, `go mod graph`, `go vet`）

### 可选工具
- `goplantuml`：struct/interface 关系提取
- `goda`：调用图分析
- `gocognit`：圈复杂度

未安装可选工具时，对应能力会降级或跳过。

## 配置

### ASCII 宽度配置

在 `.claude/settings.json` 中配置：

```json
{
  "asciiWidthCalculator": "auto",
  "asciiWidthDefault": "cjk-2x",
  "customWidthMap": {
    "CJK_BASE": 2,
    "FULLWIDTH_PUNCTUATION": 2
  }
}
```

## subagent 委派策略

**禁止在主会话中执行分析工作（summary 格式除外）。** 所有源码扫描、工具运行、数据分析必须在 subagent 中完成。

### Token 节省效果

| 场景 | 主会话直接执行 | subagent 委派 |
|------|--------------|-------------|
| 单能力 summary | ~500 token | ~100 token |
| 接口导航 JSON | ~5000 token | ~500 token |
| 全景 HTML 报告 | ~20000 token | ~300 token（文件路径） |

## 实施分期

### Phase 1（核心能力）
- ✅ SKILL.md + 渐进式文档结构
- ✅ 模块架构图（`go mod graph` + `go list`）
- ✅ 接口实现导航（正向 + 逆向）
- ✅ 代码健康度（4 个可 Shell 实现的维度）
- ✅ 4 种输出格式（HTML5 / Mermaid+ASCII / JSON / Summary）
- ✅ ASCII 宽度：终端探测 + 默认 cjk-2x

### Phase 2（增强能力）
- ⏳ 类型关系图（需 `goplantuml` 或自研 Go CLI）
- ⏳ 调用流/数据流图（需 `golang.org/x/tools/go/callgraph`）
- ⏳ 代码重复度检测（需 Go AST 分析）
- ⏳ 接口满足度报告（需 `go/types` 精确分析）
- ⏳ 趋势折线（需历史快照）
- ⏳ 增量分析（基于 `git diff`）

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 相关文档

- [SKILL.md](SKILL.md) — Skill 入口和配置
- [docs/](docs/) — 能力文档
- [docs/ref/](docs/ref/) — 参考文档
