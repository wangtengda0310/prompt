# Bencode 编码规范（实验性格式）

## 概述

Bencode 是 BitTorrent 协议使用的编码格式，用于极致压缩场景。本技能将其作为实验性格式，与 JSON 对比 token 消耗。

**重要**：此格式用于**实验对比**，非正式输出。若实测无优势则移除。

## 编码规则

### 数据类型

#### 1. 整数
格式：`i<number>e`

示例：
```
i0e      → 0
i42e     → 42
i-3e     → -3
```

#### 2. 字符串
格式：`<length>:<string>`

示例：
```
4:spam   → "spam"
0:       → ""
```

#### 3. 列表
格式：`l<contents>e`

示例：
```
l4:spam4:eggse         → ["spam", "eggs"]
li1ei2ei3ee            → [1, 2, 3]
le                     → []
```

#### 4. 字典
格式：`d<key/value pairs>e`
- 键必须是字符串
- 键必须按字典序排序

示例：
```
d3:cow3:moo4:spam4:eggse   → {"cow": "moo", "spam": "eggs"}
d4:spaml1:a1:bee           → {"spam": ["a", "b"]}
de                           → {}
```

## 项目数据编码示例

### 健康度报告
```
d                             # 字典开始
  3:chaos                     # key
  i31e                        # int 值
  4:dims                      # key
  d                           # 嵌套字典
    3:dep                     # key
    i85e                      # int 值
    3:int                     # key
    i70e                      # int 值
    3:dup                     # key
    i90e                      # int 值
    e                          # 字典结束
  4:file                      # key
  l                           # 列表开始
    d                         # 嵌套字典
      4:path                  # key
      14:handler.go           # string 值
      4:temp                  # key
      i45e                    # int 值
      e                         # 字典结束
    e                           # 列表结束
e                               # 字典结束
```

### 解码后对应 JSON
```json
{
  "chaos": 31,
  "dims": {
    "dep": 85,
    "int": 70,
    "dup": 90
  },
  "files": [
    {"path": "handler.go", "temp": 45}
  ]
}
```

## 实现示例

### Python 编码/解码
```python
import bencode

# 编码
data = {
    'chaos': 31,
    'dims': {
        'dep': 85,
        'int': 70,
        'dup': 90
    }
}

encoded = bencode.encode(data)
# b'd3:chaosi31e4:dimsd3:depi85e3:inti70ee3:dupi90eee'

# 解码
decoded = bencode.decode(encoded)
# {'chaos': 31, 'dims': {'dep': 85, 'int': 70, 'dup': 90}}
```

### Go 编码/解码
```go
import "github.com/jackpal/bencode-go"

// 编码
data := map[string]interface{}{
    "chaos": 31,
    "dims": map[string]int{
        "dep": 85,
        "int": 70,
        "dup": 90,
    },
}

var buf bytes.Buffer
err := bencode.Marshal(&buf, data)

// 解码
var decoded map[string]interface{}
err = bencode.Unmarshal(buf.Bytes(), &decoded)
```

## Token 对比实验

### 测试数据
相同项目结构使用三种编码：

#### JSON（基准）
```json
{
  "chaos": 31,
  "noise": 0.12,
  "dims": {
    "dep": 85,
    "int": 70,
    "dup": 90
  }
}
```
**字符数**：~90 字符
**估算 token**：~75 token（GPT-4）

#### Bencode
```
d3:chaosi31e4:noisef0.124:dimsd3:depi85e3:inti70e3:dupi90eee
```
**字符数**：~60 字符
**估算 token**：~50 token（GPT-4）

#### Summary
```
Chaos:31 Noise:12% Dims:dep:85/int:70/dup:90
```
**字符数**：~50 字符
**估算 token**：~35 token（GPT-4）

### 预期结果

| 格式 | 压缩率 | Token 节省 | LLM 解析成功率 |
|------|--------|-----------|--------------|
| JSON | 100% | 基准 | 100% |
| Bencode | ~67% | ~33% | 60-80%（需实测） |
| Summary | ~56% | ~53% | 95%（设计用于 LLM） |

**结论**：Bencode 可能在字符级别有压缩优势，但 LLM 分词后未必节省 token。Summary 格式专为 LLM 设计，效果最佳。

## 实验计划

1. **收集数据**：使用 10 个真实项目（小型 3 个、中型 5 个、大型 2 个）
2. **编码测试**：对每个项目生成 JSON/Bencode/Summary 三种格式
3. **Token 测量**：使用 Claude/GPT-4 的 tokenizer 测量实际 token 数
4. **解析测试**：测量 LLM 正确解析 Bencode 的成功率
5. **决策**：
   - 若 Bencode token 节省 >20% 且解析成功率 >80% → 保留
   - 否则 → 移除，使用 Summary

**结果记录位置**：`docs/ref/bencode-benchmark.md`

## 使用场景

### 当前（实验阶段）
```bash
# 启用 Bencode 实验格式
/go-model -f bencode -o report.ben
```

### 未来（若验证有效）
- subagent 间传递极简上下文
- 大型项目的缓存快照
- 需要机器解析而非人类阅读的场景

## 限制条件

1. **不支持浮点数**：Bencode 规范不包含浮点数，需转换为定点数或字符串
2. **键必须排序**：字典键必须按字典序排序
3. **UTF-8 编码**：字符串使用 UTF-8 编码，非 ASCII 字符直接编码

## 相关文档

- [输出模板](output-templates.md) — 其他输出格式
- [Bencode Benchmark](bencode-benchmark.md) — 实验结果（待生成）
