# 断言最佳实践参考

## 目录

- [核心原则](#核心原则)
- [断言粒度](#断言粒度)
- [断言消息规范](#断言消息规范)
- [断言类型选择](#断言类型选择)
- [Go/testify 用法指南](#gotestify-用法指南)
- [常见断言反模式](#常见断言反模式)
- [断言质量检查清单](#断言质量检查清单)

---

## 核心原则

### 断言的目的是什么？

1. **验证行为** — 确认被测代码的行为符合预期
2. **提供诊断** — 失败时帮助快速定位问题
3. **文档化意图** — 让测试成为可执行的文档

### 黄金法则

> **断言应该验证"行为"，而不是"实现细节"**

```go
// ❌ 验证实现细节（内部状态）
assert.Equal(t, 3, len(result.InternalList))

// ✅ 验证行为（对外可观察的结果）
assert.Equal(t, 3, result.Count())
assert.Equal(t, "item1", result.Get(0))
```

---

## 断言粒度

### 原则：一个测试验证一个行为

每个测试应该有一个清晰的"主题"——它要验证什么行为。

```go
// ✅ 好：一个测试验证一个行为
func TestParseConfig_ValidInput(t *testing.T) {
    config, err := ParseConfig("valid.yaml")

    assert.NoError(t, err)
    assert.Equal(t, "production", config.Env)
}

// ❌ 差：一个测试验证多个不相关的行为
func TestConfig(t *testing.T) {
    // 测试解析
    config, err := ParseConfig("valid.yaml")
    assert.NoError(t, err)

    // 测试验证
    assert.True(t, config.IsValid())

    // 测试序列化
    data, err := config.ToJSON()
    assert.NoError(t, err)

    // 这三个应该拆成三个独立的测试
}
```

### 允许的例外：多个相关断言

当多个断言共同验证同一个行为时，可以放在一起：

```go
// ✅ 可以接受：多个断言验证同一个"解析结果"行为
func TestParseUser(t *testing.T) {
    user, err := ParseUser(`{"name": "Alice", "age": 30}`)

    assert.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    assert.Equal(t, 30, user.Age)
    // 这些断言共同验证"用户被正确解析"这一行为
}
```

### 判断标准

问自己：**"如果这个断言失败，它描述的是什么问题？"**

- 如果答案清晰且唯一 → 粒度合适
- 如果答案模糊或多个可能 → 考虑拆分

---

## 断言消息规范

### 原则：消息应该帮助诊断，而不是重复事实

```go
// ❌ 差：消息只是重复了断言内容
assert.Equal(t, expected, result, "expected should equal result")

// ✅ 好：消息提供了上下文
assert.Equal(t, expected, result, "解析后的用户名应与输入一致")

// ✅ 好：消息指出了业务含义
assert.True(t, user.IsActive, "付费用户应该处于激活状态")
```

### 消息格式建议

| 场景 | 消息格式 | 示例 |
|------|----------|------|
| 状态验证 | "X 应该 Y" | "用户应该是激活状态" |
| 值验证 | "X 应为 Y" | "积分应为初始值 100" |
| 错误验证 | "X 不应报错" | "解析有效配置不应报错" |
| 边界验证 | "X 在 Y 条件下应 Z" | "空输入应返回空结果" |

### testify 的消息参数

testify 的断言支持可选的消息参数：

```go
// 无消息（依赖 testify 的默认输出）
assert.Equal(t, expected, result)

// 带消息（提供额外上下文）
assert.Equal(t, expected, result, "用户 ID 应保持不变")

// 带格式化消息
assert.Equal(t, expected, result, "用户 %s 的 ID 应为 %d", username, expected)
```

---

## 断言类型选择

### testify 断言类型速查

| 断言类型 | 用途 | 示例 |
|----------|------|------|
| `Equal` | 值相等 | `assert.Equal(t, 42, result)` |
| `NotEqual` | 值不等 | `assert.NotEqual(t, "", name)` |
| `True/False` | 布尔值 | `assert.True(t, isValid)` |
| `Nil/NotNil` | nil 检查 | `assert.Nil(t, err)` |
| `Empty/NotEmpty` | 集合/字符串空 | `assert.Empty(t, errors)` |
| `Len` | 集合长度 | `assert.Len(t, list, 3)` |
| `Contains/NotContains` | 包含检查 | `assert.Contains(t, msg, "error")` |
| `Error/NoError` | 错误检查 | `assert.Error(t, err)` |
| `ErrorIs` | 错误类型 | `assert.ErrorIs(t, err, ErrNotFound)` |
| `ErrorAs` | 错误类型转换 | `assert.ErrorAs(t, err, &customErr)` |
| `Implements` | 接口实现 | `assert.Implements(t, (*Reader)(nil), obj)` |
| `Type` | 类型检查 | `assert.IsType(t, &User{}, result)` |
| `ElementsMatch` | 列表元素匹配（忽略顺序） | `assert.ElementsMatch(t, expected, actual)` |
| `Subset` | 子集检查 | `assert.Subset(t, superset, subset)` |

### 选择指南

#### 1. 相等性检查

```go
// ✅ 推荐：使用 Equal（类型安全，输出清晰）
assert.Equal(t, expected, result)

// ❌ 不推荐：使用 True（错误信息不友好）
assert.True(t, expected == result)  // 失败时只显示 "expected true, got false"
```

#### 2. nil 检查

```go
// ✅ 推荐：使用 Nil/NotNil
assert.Nil(t, err)

// ❌ 不推荐：使用 Equal
assert.Equal(t, nil, err)  // 类型不安全，编译器可能警告
```

#### 3. 错误检查

```go
// 检查是否有错误
assert.Error(t, err)

// 检查是否无错误
assert.NoError(t, err)

// 检查错误类型（Go 1.13+ 错误包装）
assert.ErrorIs(t, err, ErrNotFound)

// 检查错误并提取
var customErr *CustomError
assert.ErrorAs(t, err, &customErr)
assert.Equal(t, "E001", customErr.Code)
```

#### 4. 集合检查

```go
// 检查长度
assert.Len(t, users, 3)

// 检查包含
assert.Contains(t, names, "Alice")

// 检查元素匹配（忽略顺序）
assert.ElementsMatch(t, []string{"A", "B"}, result)

// 检查子集
assert.Subset(t, allFeatures, requiredFeatures)
```

---

## Go/testify 用法指南

### 基本结构

```go
package mypackage

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestMyFunction(t *testing.T) {
    // Arrange
    input := "test"

    // Act
    result := MyFunction(input)

    // Assert
    assert.Equal(t, "expected", result)
}
```

### require vs assert

```go
import (
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestExample(t *testing.T) {
    // assert: 失败后继续执行
    assert.Equal(t, 1, 2)  // 失败，但继续
    assert.Equal(t, 3, 3)  // 仍然执行

    // require: 失败后立即终止
    require.Equal(t, 1, 2)  // 失败，测试立即终止
    // 后面的代码不会执行
}
```

**使用建议**：
- 前置条件检查用 `require`（如参数验证、初始化）
- 结果验证用 `assert`（允许多个断言都执行）

```go
func TestProcess(t *testing.T) {
    data, err := LoadData("test.json")
    require.NoError(t, err, "加载测试数据失败则无法继续")  // 前置条件

    result := Process(data)

    assert.Equal(t, "A", result.Field1)  // 结果验证
    assert.Equal(t, "B", result.Field2)  // 即使上一个失败，这个也执行
}
```

### 表驱动测试中的断言

```go
func TestValidate(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        wantErr bool
    }{
        {"有效输入", "valid", false},
        {"空输入", "", true},
        {"过长输入", strings.Repeat("x", 1000), true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := Validate(tt.input)

            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### 自定义断言

对于项目特定的断言，可以封装辅助函数：

```go
// 断言用户处于激活状态
func assertUserActive(t *testing.T, user *User, msgAndArgs ...interface{}) {
    t.Helper()  // 标记为辅助函数，错误报告正确的行号
    assert.True(t, user.IsActive, msgAndArgs...)
    assert.NotEmpty(t, user.ActivatedAt, msgAndArgs...)
    assert.Nil(t, user.SuspendedReason, msgAndArgs...)
}

// 使用
func TestUserActivation(t *testing.T) {
    user := ActivateUser(testUser)
    assertUserActive(t, user, "用户激活后应处于激活状态")
}
```

**重要**：自定义断言函数必须调用 `t.Helper()` 以确保错误报告正确的行号。

---

## 常见断言反模式

### 反模式 1：欺骗性测试

```go
// ❌ 永远通过的测试
func TestAlways(t *testing.T) {
    assert.True(t, true)  // 没有任何实际验证
}

// ❌ 不验证任何有意义的内容
func TestProcess(t *testing.T) {
    result := Process("input")
    // 没有 assert，只是确保不 panic
}
```

### 反模式 2：断言过于宽松

```go
// ❌ 太宽松
assert.NotNil(t, result)  // 只检查不为 nil，没检查值

// ✅ 更严格
assert.Equal(t, expected, result)
```

### 反模式 3：断言过于具体（耦合实现细节）

```go
// ❌ 耦合内部实现
assert.Equal(t, 5, len(user.permissions))
assert.Equal(t, "admin", user.permissions[0])

// ✅ 验证行为
assert.True(t, user.Can("admin"))
assert.True(t, user.Can("write"))
```

### 反模式 4：忽略错误

```go
// ❌ 忽略错误
result, _ := Parse("input")
assert.Equal(t, expected, result)

// ✅ 检查错误
result, err := Parse("input")
require.NoError(t, err)
assert.Equal(t, expected, result)
```

### 反模式 5：断言消息无意义

```go
// ❌ 消息重复断言内容
assert.Equal(t, 42, result, "result should be 42")

// ✅ 消息解释业务含义
assert.Equal(t, 42, result, "用户积分应为初始值 42")
```

### 反模式 6：测试间依赖

```go
// ❌ 全局状态导致测试依赖
var globalUser *User

func TestCreateUser(t *testing.T) {
    globalUser = CreateUser()  // 后续测试依赖这个
}

func TestUpdateUser(t *testing.T) {
    UpdateUser(globalUser)  // 如果 TestCreateUser 先运行才工作
}

// ✅ 每个测试独立
func TestUpdateUser(t *testing.T) {
    user := createTestUser()  // 独立创建
    UpdateUser(user)
}
```

---

## 断言质量检查清单

生成测试后，逐项检查断言质量：

### 基本检查

- [ ] 每个测试至少有一个断言
- [ ] 断言验证的是行为，不是实现细节
- [ ] 断言失败时有清晰的诊断信息
- [ ] 没有忽略错误返回值
- [ ] 没有欺骗性测试（assert.True(true)）

### 粒度检查

- [ ] 一个测试验证一个行为（或一组紧密相关的断言）
- [ ] 测试名称准确描述了断言内容
- [ ] 不相关的断言已拆分到独立测试

### 消息检查

- [ ] 断言消息提供了业务上下文（而非重复断言内容）
- [ ] 消息帮助理解"为什么"这个值应该是这样
- [ ] 表驱动测试的用例名清晰描述了场景

### 类型选择检查

- [ ] 使用 Equal 而非 True 检查相等性
- [ ] 使用 Nil/NotNil 而非 Equal 检查 nil
- [ ] 使用 ErrorIs/ErrorAs 检查特定错误
- [ ] 使用 Len 检查集合长度

### 独立性检查

- [ ] 测试不依赖全局状态
- [ ] 测试不依赖执行顺序
- [ ] 每个测试独立准备自己的数据
- [ ] 测试之间没有共享的可变状态

---

## 附录：testify/assert 完整 API 参考

最常用的断言（按使用频率排序）：

| 断言 | 用途 |
|------|------|
| `Equal` / `NotEqual` | 值比较 |
| `NoError` / `Error` | 错误检查 |
| `True` / `False` | 布尔检查 |
| `Nil` / `NotNil` | nil 检查 |
| `Empty` / `NotEmpty` | 空/非空检查 |
| `Len` | 长度检查 |
| `Contains` / `NotContains` | 包含检查 |
| `ErrorIs` / `ErrorAs` | 错误类型检查 |
| `ElementsMatch` | 列表元素匹配（忽略顺序） |
| `Greater` / `Less` | 大小比较 |
| `Implements` | 接口实现检查 |
| `IsType` | 类型检查 |
| `Panics` / `NotPanics` | panic 检查 |
| `WithinDuration` | 时间差检查 |
| `Regexp` / `NotRegexp` | 正则匹配 |

官方文档：https://pkg.go.dev/github.com/stretchr/testify/assert
