# {PACKAGE_NAME} - 类型定义图

## 类型层级结构

```mermaid
classDiagram
    {TYPE_DEFINITIONS}
    {TYPE_RELATIONSHIPS}
```

## 接口实现关系

```mermaid
graph TD
    {INTERFACE_IMPLEMENTATIONS}

    classDef interface fill:#b794f6,stroke:#7c3aed,color:#fff;
    classDef struct fill:#4a9eff,stroke:#2563eb,color:#fff;
    classDef alias fill:#4ade80,stroke:#16a34a,color:#fff;

    {INTERFACE_CLASSES}
```

## 类型详情

### 结构体

| 名称 | 字段数 | 方法数 | 导出字段 | 导出方法 |
|------|--------|--------|----------|----------|
{STRUCT_TABLE_ROWS}

### 接口

| 名称 | 方法数 | 导出方法 | 实现者数量 |
|------|--------|----------|------------|
{INTERFACE_TABLE_ROWS}

### 类型别名

| 原名称 | 别名 | 用途 |
|--------|------|------|
{ALIAS_TABLE_ROWS}

## 方法分布

```mermaid
pie title 各类型方法数量分布
    {METHOD_DISTRIBUTION}
```

## 复杂度分析

| 类型 | 圈复杂度 | 继承深度 | 耦合度 | 评级 |
|------|----------|----------|--------|------|
{COMPLEXITY_TABLE_ROWS}
