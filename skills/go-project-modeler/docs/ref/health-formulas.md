# 健康度评分公式详解

## 概述

本文档定义代码健康度各维度的详细计算公式，采用线性扣分机制避免二元阈值的不合理评分。

## 通用公式

### 线性扣分函数
```
score = max(0, base - (value - threshold) * penalty)
```

参数说明：
- `base`：基础分数（通常 100）
- `value`：实际测量值
- `threshold`：阈值起点
- `penalty`：每超 1 单位的扣分

## 维度 1：依赖复杂度（20%）

### 子指标 1.1：依赖深度
```
depthScore = max(0, 100 - (maxDepth - 4) * 10)
```
- `maxDepth`：最长依赖链长度
- 阈值：4 层
- 扣分：每超 1 层扣 10 分

### 子指标 1.2：环路数量
```
hasCycle = cycleCount > 0 ? 0 : 100
```
- 存在循环依赖直接记 0 分
- 无环路则 100 分

### 子指标 1.3：扇入扇出比
```
ratioScore = max(0, 100 - (fanOut - fanIn) * 5)
```
- `fanOut`：依赖数（出度）
- `fanIn`：被依赖数（入度）
- 扇出远大于扇入表明过度依赖

### 综合评分
```
depScore = (depthScore * 0.4 + hasCycle * 0.3 + ratioScore * 0.3)
```

## 维度 2：接口清晰度（20%）

### 子指标 2.1：接口方法数
```
methodScore = max(0, 100 - (avgMethods - 5) * 10)
```
- `avgMethods`：平均接口方法数
- 阈值：5 个方法
- 扣分：每超 1 个扣 10 分

### 子指标 2.2：空接口占比
```
emptyScore = 100 - (emptyCount / totalCount) * 100
```
- `emptyCount`：无实现的接口数
- `totalCount`：接口总数

### 子指标 2.3：鸭子类型密度
```
duckScore = max(0, 100 - implicitImplRatio * 50)
```
- `implicitImplRatio`：隐式实现比例
- 隐式实现越多，追溯越困难

### 综合评分
```
interfaceScore = (methodScore * 0.5 + emptyScore * 0.3 + duckScore * 0.2)
```

## 维度 3：代码重复度（20%）

### Token 序列相似度
使用 Jaccard 相似系数：
```
similarity(A, B) = |A ∩ B| / |A ∪ B|
```

### 重复率计算
```
duplicationRate = totalDupTokens / totalTokens * 100
dupScore = max(0, 100 - duplicationRate * 2)
```
- `totalDupTokens`：重复代码 token 总数
- `totalTokens`：项目总 token 数
- 扣分：重复率每 1% 扣 2 分

### 重复类型
1. **完全重复**：相同代码块
2. **结构重复**：相同逻辑结构
3. **模式重复**：相同设计模式

## 维度 4：结构复杂度（15%）

### 子指标 4.1：结构体方法数
```
structMethodScore = max(0, 100 - (avgMethods - 9) * 5)
```
- 阈值：9 个方法（来自项目编码规范）
- 扣分：每超 1 个扣 5 分

### 子指标 4.2：嵌套深度
```
nestingScore = max(0, 100 - (maxNesting - 3) * 10)
```
- 阈值：3 层嵌套
- 扣分：每超 1 层扣 10 分

### 子指标 4.3：圈复杂度
使用 `gocognit` 工具测量：
```
complexityScore = max(0, 100 - (avgCyclomatic - 10) * 3)
```
- 阈值：10（McCabe 复杂度标准）
- 扣分：每超 1 扣 3 分

### 综合评分
```
complexityScore = (structMethodScore * 0.4 + nestingScore * 0.3 + complexityScore * 0.3)
```

## 维度 5：文件膨胀度（15%）

### 子指标 5.1：文件行数
```
lineScore = max(0, 100 - (avgLines - 500) / 10)
```
- 阈值：500 行
- 扣分：每超 100 行扣 10 分

### 子指标 5.2：结构体数量
```
structScore = max(0, 100 - (avgStructs - 3) * 15)
```
- 阈值：3 个结构体（来自项目编码规范）
- 扣分：每超 1 个扣 15 分

### 子指标 5.3：函数数量
```
funcScore = max(0, 100 - (avgFuncs - 20) * 2)
```
- 阈值：20 个函数
- 扣分：每超 1 个扣 2 分

### 综合评分
```
bloatScore = (lineScore * 0.5 + structScore * 0.3 + funcScore * 0.2)
```

## 维度 6：死代码率（10%）

### 死代码检测
```
deadRatio = deadTokens / totalTokens
deadScore = max(0, 100 - deadRatio * 100 * 2)
```
- `deadTokens`：未引用代码 token 数
- 扣分：死代码每 1% 扣 2 分

### 死代码类型
1. **未导出且未引用**：`func unused()`
2. **不可达代码**：`return` 后的语句
3. **冗余分支**：`if true { ... }`

## 综合健康度

### 混乱指数（ChaosIndex）
```
ChaosIndex = 100 - WeightedAvg(各维度分数)

权重分配：
- 依赖复杂度：20%
- 接口清晰度：20%
- 代码重复度：20%
- 结构复杂度：15%
- 文件膨胀度：15%
- 死代码率：10%
```

### 噪音率（NoiseRatio）
```
NoiseRatio = (DeadCode + DuplicatedCode) / TotalCode
```

## 分级标准

| ChaosIndex | 等级 | 颜色 | 行动建议 |
|-----------|------|------|---------|
| 0-20 | 健康 | 绿色 | 保持现有实践 |
| 21-40 | 关注 | 黄色 | 定期监控，预防恶化 |
| 41-60 | 混乱 | 橙色 | 规划重构，优先处理高分项 |
| 61-100 | 失控 | 红色 | 紧急重构，或考虑重写 |

## 热力图温度计算

文件级温度：
```
temperature = max(
    (lines - 500) / 10,
    (structs - 3) * 5,
    (funcs - 20) * 2,
    complexity - 10,
    deadRatio * 100
)
temperature = max(15, min(100, 15 + temperature))
```

温度映射：
- 15-30°C：绿色（健康）
- 31-60°C：黄色（关注）
- 61-100°C：红色（混乱）

## 相关文档

- [代码健康度/噪声度](../health-metrics.md) — 使用指南
