# 游戏配表分析技能 - 详细文档索引

本文档目录提供游戏配表分析技能的完整功能说明和详细参考。

## 文档导航

### 核心功能
- **[01-core-analysis.md](01-core-analysis.md)** - 核心分析功能详解
  - 配表扫描与结构分析
  - 表关系分析方法
  - 约束规则提取
  - 实现技巧与最佳实践

### 分析增强
- **[02-diff-impact.md](02-diff-impact.md)** - 差异与影响分析
  - 配表版本对比
  - 影响范围评估
  - 依赖追溯

### 验证功能
- **[03-validation.md](03-validation.md)** - 验证引擎
  - 数据完整性验证
  - 一致性验证
  - 业务规则验证

### 交互工具
- **[04-interactive.md](04-interactive.md)** - 交互工具
  - 全文搜索功能
  - 批量操作
  - 配置模拟器

### 可视化
- **[05-visualization.md](05-visualization.md)** - 可视化增强
  - 交互式图表
  - 热力图
  - 时间线视图

### AI 功能
- **[06-ai-features.md](06-ai-features.md)** - AI 功能
  - 智能推荐
  - 自然语言查询
  - 反模式检测

### 基础设施
- **[07-memory-storage.md](07-memory-storage.md)** - 记忆存储
  - 记忆类型与优先级
  - 存储策略
  - 记忆更新机制

- **[08-tool-selection.md](08-tool-selection.md)** - 工具选择策略
  - 工具检测方法
  - 优先级规则
  - 兼容性处理

## 快速查找

### 按场景查找
| 场景 | 参考文档 |
|------|----------|
| 分析新项目配表 | 01-core-analysis.md |
| 对比版本差异 | 02-diff-impact.md |
| 验证配表正确性 | 03-validation.md |
| 搜索特定配置 | 04-interactive.md |
| 生成可视化报告 | 05-visualization.md |
| 获取优化建议 | 06-ai-features.md |
| 了解记忆机制 | 07-memory-storage.md |
| 配置本地工具 | 08-tool-selection.md |

### 按问题查找
| 问题 | 参考文档 |
|------|----------|
| 如何开始分析？ | 01-core-analysis.md - 快速开始 |
| 关系分析不准确？ | 01-core-analysis.md - 关系识别模式 |
| 如何对比版本？ | 02-diff-impact.md - 差异分析 |
| 修改影响评估？ | 02-diff-impact.md - 影响分析 |
| 验证失败处理？ | 03-validation.md - 错误处理 |
| 如何批量修改？ | 04-interactive.md - 批量操作 |
| 图表不显示？ | 05-visualization.md - 故障排除 |
| 记忆存储在哪？ | 07-memory-storage.md - 存储位置 |
| 使用哪个工具？ | 08-tool-selection.md - 选择流程 |

## 文档使用说明

### 阅读顺序建议

**初学者**：
1. 阅读主 SKILL.md 了解基本功能
2. 参考 01-core-analysis.md 开始第一次分析
3. 根据需要深入其他文档

**进阶用户**：
1. 直接查阅相关功能文档
2. 参考 02-06 各专题文档
3. 深入了解 07-08 基础设施

**开发者**：
1. 先阅读 08-tool-selection.md 了解架构
2. 参考 07-memory-storage.md 理解存储机制
3. 研究各功能脚本的实现

### 文档约定

- **代码块** - 表示命令行示例或代码
- **表格** - 表示配置选项、类型说明等
- **Mermaid 图表** - 表示流程图或关系图
- **⚠️ 警告** - 表示需要注意的问题
- **✅ 推荐** - 表示最佳实践

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2025-01 | 初始版本，支持核心分析功能 |
