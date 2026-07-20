# 输出格式模板

## 概述

本文档定义各输出格式的完整模板结构，确保输出的一致性和可解析性。

## 1. HTML5 交互页面

### 文件结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Go 项目建模器 - {{ProjectName}}</title>
    <style>
        /* 内联 CSS */
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --border-color: #e0e0e0;
            --highlight-color: #4a90e2;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #1e1e1e;
                --text-color: #e0e0e0;
                --border-color: #3a3a3a;
                --highlight-color: #64b5f6;
            }
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        /* ... 更多样式 ... */
    </style>
</head>
<body>
    <header>
        <h1>{{ProjectName}} - 项目架构分析</h1>
        <nav>
            <button data-view="architecture">架构图</button>
            <button data-view="types">类型关系</button>
            <button data-view="interfaces">接口导航</button>
            <button data-view="callflow">调用流</button>
            <button data-view="health">健康度</button>
        </nav>
    </header>

    <main id="content">
        <!-- 视图容器 -->
    </main>

    <script>
        // 内联 JavaScript
        const data = {{EmbeddedJSON}};
        // ... 交互逻辑 ...
    </script>
</body>
</html>
```

### JavaScript 交互
```javascript
// 视图切换
document.querySelectorAll('nav button').forEach(btn => {
    btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        loadView(view);
        updateHash(view);
    });
});

// SVG 缩放/拖拽
const svg = document.querySelector('svg');
let transform = {x: 0, y: 0, scale: 1};

svg.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    transform.scale *= delta;
    updateTransform();
});

// 搜索高亮
document.getElementById('search').addEventListener('input', (e) => {
    const query = e.target.value;
    highlightNodes(query);
});

// 深链接
window.addEventListener('hashchange', () => {
    const hash = window.location.hash;
    if (hash) {
        const params = new URLSearchParams(hash.slice(1));
        const view = params.get('view');
        const file = params.get('file');
        loadView(view, file);
    }
});
```

## 2. Mermaid 图表

### 架构图模板
```mermaid
graph TD
    %% 自动生成部分
    {{#each packages}}
    {{@key}}[{{name}}]
    {{/each}}

    %% 依赖关系
    {{#each dependencies}}
    {{from}} -->|{{label}}| {{to}}
    {{/each}}

    %% 样式
    classDef healthy fill:#90EE90
    classDef warning fill:#FFD700
    classDef critical fill:#FF6B6B

    {{#each styledNodes}}
    class {{id}} {{style}}
    {{/each}}
```

### 类型关系图模板
```mermaid
classDiagram
    {{#each structs}}
    class {{name}}{
        {{#each fields}}
        {{visibility}} {{name}} {{type}}
        {{/each}}
        {{#each methods}}
        {{visibility}} {{name}}({{params}}) {{returns}}
        {{/each}}
    }
    {{/each}}

    {{#each relationships}}
    {{parent}} <|-- {{child}}
    {{/each}}
```

### 调用流图模板
```mermaid
graph LR
    {{#each calls}}
    {{from}}[{{fromName}}] -->|{{label}}| {{to}}[{{toName}}]
    {{/each}}
```

## 3. ASCII 文本图

### 架构图模板
```
{{#each modules}}
┌─────────────────────────────┐
│  {{name}}                   │
│  {{path}}                   │
└───────────┬─────────────────┘
{{/each}}
```

### 宽度计算
```python
def calculate_width(text, calculator='cjk-2x'):
    width = 0
    for char in text:
        if calculator == 'cjk-2x':
            if '\u4e00' <= char <= '\u9fff':  # CJK
                width += 2
            else:
                width += 1
        elif calculator == 'wcwidth':
            width += wcwidth(char)
        elif calculator == 'en':
            width += 1
    return width
```

## 4. JSON 结构化数据

### 完整报告结构
```json
{
  "meta": {
    "project": "github.com/user/project",
    "timestamp": "2026-04-09T12:00:00Z",
    "version": "1.0.0"
  },
  "architecture": {
    "modules": [
      {
        "path": "github.com/user/project/cmd",
        "name": "cmd",
        "dependencies": ["github.com/user/project/internal"]
      }
    ],
    "cycles": [
      ["pkgA", "pkgB", "pkgA"]
    ]
  },
  "types": {
    "structs": [
      {
        "name": "ActivityChecker",
        "file": "checker.go",
        "fields": [
          {"name": "BaseChecker", "embedded": true}
        ],
        "methods": ["Check", "Name"]
      }
    ],
    "embedding": [
      ["ActivityChecker", "BaseChecker", "Validator"]
    ]
  },
  "interfaces": {
    "checker": {
      "name": "Checker",
      "methods": ["Check() error", "Name() string"],
      "implementations": [
        {"struct": "ActivityChecker", "file": "activity/checker.go"}
      ]
    }
  },
  "callflow": {
    "nodes": [
      {"id": "main", "type": "function", "file": "main.go", "line": 10}
    ],
    "edges": [
      {"from": "main", "to": "LoadExcel", "label": "calls"}
    ]
  },
  "health": {
    "chaos": 31,
    "noise": 0.12,
    "dimensions": {
      "dependency": 85,
      "interface": 70,
      "duplicate": 90,
      "complexity": 60,
      "bloat": 75,
      "dead": 95
    },
    "worst_files": [
      {"path": "handler.go", "temperature": 45, "issues": ["lines>500"]}
    ]
  }
}
```

### 紧凑模式
```json
{
  "p": "github.com/user/project",
  "t": "2026-04-09T12:00:00Z",
  "h": {
    "c": 31,
    "n": 0.12,
    "d": {"dep":85,"int":70,"dup":90,"cmp":60,"blt":75,"ded":95}
  }
}
```

## 5. Summary 摘要

### 模板
```
{{ProjectName}} - 项目概况

架构: {{ModuleCount}} 模块, {{PackageCount}} 包
健康度: {{ChaosIndex}} ({{Grade}})
噪音率: {{NoiseRatio}}%

最复杂文件:
{{#each worstFiles}}
  - {{path}} ({{temperature}}°C)
{{/each}}

依赖深度: {{MaxDepth}}
循环依赖: {{CycleCount}}
未覆盖测试: {{UncoveredRatio}}%

生成时间: {{Timestamp}}
```

### 示例输出
```
rain-excel-checker - 项目概况

架构: 3 模块, 12 包
健康度: 31 (关注)
噪音率: 12%

最复杂文件:
  - xlsx/parser.go (45°C)
  - rules/engine.go (38°C)

依赖深度: 5
循环依赖: 0
未覆盖测试: 45%

生成时间: 2026-04-09 12:00:00
```

## 6. Bencode 格式（实验性）

### 编码规范
```
d                   # 字典开始
  3:chaos           # key
  i31e              # int 值
  4:dims            # key
  d                 # 嵌套字典
    3:dep           # key
    i85e            # int 值
    e               # 字典结束
  e                 # 字典结束
e                   # 字典结束
```

### 解析示例
```python
import bencode

data = {
    'chaos': 31,
    'noise': 0.12,
    'dims': {
        'dep': 85,
        'int': 70
    }
}

encoded = bencode.encode(data)
# b'd3:chaosi31e4:dimsd3:depi85e3:inti70eee4:noisef0.12e'
```

## 输出选择逻辑

```python
def select_format(user_spec, caller_type):
    if user_spec:
        return user_spec
    if caller_type == 'subagent':
        return 'summary'
    if caller_type == 'human':
        return 'html'
    return 'auto'
```

## 相关文档

- [提取工具技术细节](extractor-details.md) — 数据来源
- [ASCII 中文宽度](../ascii-width.md) — 宽度计算
