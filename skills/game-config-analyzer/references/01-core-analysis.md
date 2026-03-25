# 核心分析功能详解

本文档详细说明游戏配表分析技能的核心分析功能。

## 目录

- [配表扫描](#配表扫描)
- [结构分析](#结构分析)
- [关系分析](#关系分析)
- [约束提取](#约束提取)
- [实现技巧](#实现技巧)

---

## 配表扫描

### 扫描方法

```python
analyzer = ConfigAnalyzer(config_dir)
scan_result = analyzer.scan_directory()
```

### 扫描输出

```json
{
  "files": [
    {
      "filename": "Hero.xlsx",
      "path": "/path/to/Hero.xlsx",
      "sheets": [
        {
          "name": "Hero",
          "headers": [
            {
              "column": 1,
              "chs_name": "英雄ID",
              "type": "int",
              "name": "Id",
              "export": "server"
            }
          ],
          "row_count": 152,
          "header_row": 4
        }
      ]
    }
  ],
  "total_count": 10,
  "sheets_count": 12
}
```

### 表头格式识别

标准配表使用 4 行表头格式：

| 行号 | 内容 | 示例 |
|------|------|------|
| 1 | 中文名 | 英雄ID |
| 2 | 数据类型 | int |
| 3 | 字段名 | Id |
| 4 | 导出标识 | server/client |

### 非标准格式处理

```python
def _find_header_row(self, sheet) -> int:
    """查找表头行"""
    # 1. 检查 server/client 标记
    for row_idx in range(1, 10):
        for cell in sheet[row_idx]:
            if cell.value and 'server/client' in str(cell.value):
                return row_idx - 1

    # 2. 默认第 4 行
    return 4
```

---

## 结构分析

### 字段类型推断

```python
def infer_field_type(header: Dict) -> str:
    """推断字段类型"""
    field_type = header.get("type", "").lower()
    field_name = header.get("name", "").lower()

    if "int" in field_type:
        return "integer"
    elif "string" in field_type or "str" in field_type:
        return "string"
    elif "float" in field_type or "double" in field_type:
        return "float"
    elif "time" in field_name or "date" in field_name:
        return "datetime"
    elif "bool" in field_type:
        return "boolean"

    return "unknown"
```

### 表分类

| 类型 | 定义 | 特征 |
|------|------|------|
| 中心表 | 被多个表引用 | ID 被引用次数 > 3 |
| 边缘表 | 引用其他表 | 有 ID 引用，不被引用 |
| 枚举表 | 提供枚举值 | 表名以 E 开头 |
| 孤立表 | 无关联关系 | 无引用关系 |

---

## 关系分析

### 关系识别模式

#### 1. ID 引用

```python
# XxxId -> Xxx.Id
"HeroId" -> Hero 表的 Id 字段
"SkillIds" -> Skill 表的 Id 字段（数组）
```

#### 2. 枚举引用

```python
# E#枚举名
"E#DamageType" -> EDamageType 枚举表
"E#Country" -> ECountry 枚举表
```

#### 3. 时间约束

```python
# 时间同步
"OpenDate" = "SeasonStartTime"  # 大将军武将
"OpenDate" ∈ ["StartTime", "EndTime"]  # 战令武将
```

#### 4. 物品 ID 解析

```python
# 物品 ID 格式: {类型;子类型}
"{1010804;1}" -> 类型=1010804, 子类型=1
```

### 关系图生成

```python
def generate_mermaid_graph(relations: List[Dict]) -> str:
    """生成 Mermaid 关系图"""
    lines = ["graph TD"]

    # 节点分类
    center_tables = get_center_tables(relations)
    edge_tables = get_edge_tables(relations)
    enum_tables = get_enum_tables(relations)

    # 生成节点和关系
    for rel in relations:
        # 添加样式标记
        ...

    return "\n".join(lines)
```

---

## 约束提取

### 约束类型

#### 1. 时间约束

| 约束 | 规则 | 示例 |
|------|------|------|
| 顺序约束 | StartTime < EndTime | 活动时间 |
| 范围约束 | OpenDate ∈ [Start, End] | 战令武将 |
| 同步约束 | OpenDate = SeasonStartTime | 大将军武将 |

#### 2. 数值约束

```python
# 范围约束
"Level" ∈ [1, 100]

# 倍数关系
"RewardCount" % 10 == 0
```

#### 3. 引用约束

```python
# 外键存在性
"HeroId" ∈ Hero.Id

# 数组引用
"SkillIds" ⊆ Skill.Id
```

#### 4. 条件约束

```python
# 条件依赖
IsOpen == true → OpenDate != null

# 组合约束
Type == "SeasonPass" → OpenDate ∈ [StartTime, EndTime]
```

### 约束表示例

| 源表.字段 | 约束类型 | 约束规则 | 依赖表 |
|-----------|----------|----------|--------|
| Hero.OpenDate | 时间约束 | 战令武将 ∈ [SeasonPass.StartTime, EndTime] | SeasonPass |
| Hero.OpenDate | 时间约束 | 大将军武将 = ArenaSeason.SeasonStartTime | ArenaSeason |
| Activity.StartTime | 顺序约束 | StartTime < EndTime | - |
| Hero.Skills | 引用约束 | Skills ⊆ Skill.Id | Skill |

---

## 实现技巧

### 1. 渐进式分析

```python
def progressive_analysis(config_dir):
    """渐进式分析"""
    # 第 1 轮: 快速扫描
    quick_scan = scan_only_structure(config_dir)

    # 第 2 轮: 深度分析
    deep_analysis = analyze_relations_and_constraints(quick_scan)

    # 第 3 轮: 验证和生成
    validation = validate_all_rules(deep_analysis)
    generate_reports(validation)
```

### 2. 缓存机制

```python
class CachedAnalyzer(ConfigAnalyzer):
    """带缓存的的分析器"""

    def __init__(self, config_dir):
        super().__init__(config_dir)
        self._cache = {}

    def analyze_file(self, file_path):
        cache_key = str(file_path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = super()._analyze_file(file_path)
        self._cache[cache_key] = result
        return result
```

### 3. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_scan(config_dir, max_workers=4):
    """并行扫描"""
    files = list(Path(config_dir).rglob("*.xlsx"))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(analyze_single_file, files)

    return [r for r in results if r]
```

---

## 最佳实践

### 分析流程

```
1. 快速扫描（1-2 分钟）
   ├─ 收集配表清单
   ├─ 提取表头结构
   └─ 统计基本信息

2. 关系分析（2-5 分钟）
   ├─ 构建 ID 引用关系
   ├─ 识别时间约束
   └─ 检测循环引用

3. 约束提取（5-10 分钟）
   ├─ 提取时间约束规则
   ├─ 提取引用约束规则
   └─ 提取业务规则

4. 文档生成（2-3 分钟）
   ├─ 生成关系图
   ├─ 生成约束表
   └─ 生成分析报告
```

### 大型项目处理

对于 100+ 配表的项目：

1. **分模块分析**
   ```python
   modules = {
       "core": ["Hero", "Skill", "Card"],
       "gameplay": ["Arena", "Campaign", "Challenge"],
       "system": ["Activity", "SeasonPass", "Task"]
   }
   ```

2. **增量更新**
   ```python
   # 只分析变更的配表
   changed_files = detect_changes(last_analysis_time)
   incremental_update(changed_files)
   ```

3. **分层文档**
   ```
   总览文档 (index.md)
   ├── 核心系统分析.md
   ├── 玩法系统分析.md
   └── 独立系统分析.md
   ```
