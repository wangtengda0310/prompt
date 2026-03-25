# 快速参考

本文档提供所有脚本和功能的快速参考。

## 脚本列表

| 脚本 | 功能 | Phase |
|------|------|-------|
| `analyzer.py` | 核心分析 | 1 |
| `diff_analyzer.py` | 差异分析 | 2 |
| `impact_analyzer.py` | 影响分析 | 2 |
| `validator.py` | 数据验证 | 3 |
| `search.py` | 全文搜索 | 4 |
| `batch_operator.py` | 批量操作 | 4 |
| `simulator.py` | 配置模拟器 | 4 |
| `smart_recommender.py` | 智能推荐 | 6 |
| `anti_pattern_detector.py` | 反模式检测 | 6 |

## 命令速查

### 核心分析

```bash
# 扫描配表目录
python scripts/analyzer.py <配表目录>

# 输出文件
# - scan_result.json
# - relations.json
# - constraints.json
# - analysis_report.md
```

### 差异分析

```bash
# 对比两个版本
python scripts/diff_analyzer.py <目录A> <目录B>

# 输出文件
# - diff_report.json
# - diff_report.md
```

### 影响分析

```bash
# 评估变更影响
python scripts/impact_analyzer.py <关系.json> <变更.json>

# 输出文件
# - impact_report.json
# - impact_report.md
```

### 数据验证

```bash
# 验证配表数据
python scripts/validator.py <配表目录> [分析.json]

# 输出文件
# - validation_report.json
# - validation_report.md
```

### 全文搜索

```bash
# 模糊搜索 (默认)
python scripts/search.py <配表目录> <查询>

# 精确搜索
python scripts/search.py <配表目录> <查询> exact

# 正则搜索
python scripts/search.py <配表目录> <正则> regex

# 字段限定搜索
python scripts/search.py <配表目录> "field:value" field
```

### 批量操作

```bash
# 添加字段
python scripts/batch_operator.py <配表目录> add <表列表> <字段定义.json>

# 删除字段
python scripts/batch_operator.py <配表目录> remove <表列表> <字段名>

# 更新值
python scripts/batch_operator.py <配表目录> update <表名> <条件.json> <更新.json>

# 预览操作
python scripts/batch_operator.py <配表目录> preview <操作.json>
```

### 配置模拟器

```bash
# 单表变更模拟
python scripts/simulator.py <关系.json> <变更.json>

# 批量变更模拟
python scripts/simulator.py <关系.json> <批量变更.json>
```

### 智能推荐

```bash
# 生成优化建议
python scripts/smart_recommender.py <分析.json> [输出.json]
```

### 反模式检测

```bash
# 检测反模式
python scripts/anti_pattern_detector.py <分析.json> [输出.json]
```

## 常见工作流

### 新项目分析

```bash
# 1. 扫描配表
python scripts/analyzer.py ./configs

# 2. 生成推荐
python scripts/smart_recommender.py scan_result.json

# 3. 检测反模式
python scripts/anti_pattern_detector.py scan_result.json
```

### 版本对比

```bash
# 对比两个版本
python scripts/diff_analyzer.py ./configs/v1 ./configs/v2
```

### 变更评估

```bash
# 1. 分析当前版本
python scripts/analyzer.py ./configs > analysis.json

# 2. 评估变更影响
python scripts/impact_analyzer.py relations.json changes.json

# 3. 验证变更后数据
python scripts/validator.py ./configs_new
```

### 数据质量检查

```bash
# 完整验证流程
python scripts/validator.py ./configs
```

## 输出文件说明

| 文件 | 内容 | 格式 |
|------|------|------|
| `scan_result.json` | 扫描结果 | JSON |
| `relations.json` | 表关系 | JSON |
| `constraints.json` | 约束规则 | JSON |
| `*_report.md` | 分析报告 | Markdown |
| `*_report.json` | 详细数据 | JSON |

## 约束类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `time_order` | 时间顺序 | StartTime < EndTime |
| `time_range` | 时间范围 | OpenDate ∈ [Start, End] |
| `range` | 数值范围 | Level ∈ [1, 100] |
| `enum` | 枚举约束 | Type ∈ {1, 2, 3} |
| `reference` | 引用完整性 | HeroId ∈ Hero.Id |
| `conditional` | 条件约束 | IsOpen=true → OpenDate≠null |

## 关系类型

| 类型 | 说明 | 检测方式 |
|------|------|----------|
| 直接引用 | A.字段 → B.主键 | `XxxId` → `Xxx.Id` |
| 时间约束 | A.时间 ∈ B.范围 | 字段名匹配 |
| 枚举约束 | A.字段 = B.枚举 | 类型+命名匹配 |

## 反模式类型

| 反模式 | 严重度 | 阈值 |
|--------|--------|------|
| 循环引用 | 🔴 高 | 检测环路 |
| 孤立表 | 🔵 信息 | 无关联 |
| 过度依赖 | 🟡 中 | 引用 >10 表 |
| 深度嵌套 | 🟡 中 | 深度 >5 |
| 贫血模型 | 🟢 低 | ID 占比 >80% |

## 推荐类型

| 类型 | 优先级 | 触发条件 |
|------|--------|----------|
| structure | 高/中/低 | 大表、多字段 |
| constraint | 高 | 外键、时间对 |
| naming | 低 | 命名不一致 |
| performance | 中/低 | 热表、多引用 |
| quality | 低 | 冗余字段 |

## 进阶使用

### Python API

```python
# 核心分析
from scripts.analyzer import ConfigAnalyzer

analyzer = ConfigAnalyzer(config_dir)
result = analyzer.scan_all()
analyzer.save_results("output.json")

# 关系分析
from scripts.analyzer import RelationAnalyzer

relation_analyzer = RelationAnalyzer(scan_result)
relations = relation_analyzer.analyze_relations()

# 验证
from scripts.validator import ConfigValidator

validator = ConfigValidator(config_dir, scan_result, relations, constraints)
results = validator.validate_all()
```

### 自定义规则

```python
# 添加自定义约束
custom_constraints = [
    {
        "table": "Hero",
        "field": "Level",
        "type": "range",
        "rule": {"min": 1, "max": 100},
        "message": "英雄等级必须在 1-100 之间"
    }
]

validator = ConfigValidator(config_dir, constraints=custom_constraints)
```

## 故障排除

### 问题：无法打开 Excel 文件

```
错误: BadZipFile
解决: 确保文件未被其他程序打开，检查文件格式
```

### 问题：表头识别错误

```
错误: 无法找到表头行
解决: 检查配表是否符合标准格式 (4行表头)
```

### 问题：关系分析不准确

```
解决:
1. 检查字段命名是否规范
2. 使用 `--strict` 模式
3. 手动补充关系定义
```

### 问题：内存占用过高

```
解决:
1. 使用 `--limit` 限制处理行数
2. 分批处理大文件
3. 使用搜索而非全量扫描
```
