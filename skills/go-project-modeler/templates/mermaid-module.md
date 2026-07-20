# {PROJECT_NAME} - 模块依赖图

## 依赖关系图

```mermaid
graph TD
    {MODULE_NODES}
    {MODULE_EDGES}

    classDef mainModule fill:#4a9eff,stroke:#2980b9,color:#fff;
    classDep dependency fill:#e0e0e0,stroke:#95a5a6,color:#333;
    class external fill:#f8f9fa,stroke:#dee2e6,color:#495057;

    {MODULE_CLASSES}
```

## 模块说明

| 模块名 | 路径 | 包数 | 依赖数 | 被依赖数 |
|--------|------|------|--------|----------|
{MODULE_TABLE_ROWS}

## 依赖层次

```mermaid
graph LR
    {LAYER_NODES}
    {LAYER_EDGES}

    classDef layer0 fill:#4a9eff,stroke:#2980b9,color:#fff;
    classDef layer1 fill:#5dade2,stroke:#2980b9,color:#fff;
    classDef layer2 fill:#85c1e9,stroke:#2980b9,color:#fff;
    classDef layer3 fill:#aed6f1,stroke:#2980b9,color:#fff;

    {LAYER_CLASSES}
```

## 循环依赖检测

{CIRCULAR_DEPENDENCIES}

## 外部依赖

| 依赖包 | 版本 | 用途 |
|--------|------|------|
{EXTERNAL_DEPENDENCIES}
