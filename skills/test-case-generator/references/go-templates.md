# Go 测试模板参考

## 目录

- [单元测试模板](#单元测试模板)
- [表驱动测试模板](#表驱动测试模板)
- [集成测试模板](#集成测试模板)
- [回归测试模板](#回归测试模板)
- [规则测试模板（Excel 检查器）](#规则测试模板)
- [机器人测试模板（rain-robot）](#机器人测试模板)

---

## 单元测试模板

```go
package mypackage

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

// Test<FunctionName>_<Scenario> 测试<功能描述>
func TestFunctionName_NormalCase(t *testing.T) {
    // Arrange - 准备测试数据
    input := "valid-input"
    expected := "expected-output"

    // Act - 执行被测函数
    result, err := MyFunction(input)

    // Assert - 验证结果
    assert.NoError(t, err)
    assert.Equal(t, expected, result)
}

// Test<FunctionName>_InvalidInput 测试无效输入
func TestFunctionName_InvalidInput(t *testing.T) {
    result, err := MyFunction("")

    assert.Error(t, err)
    assert.Empty(t, result)
}
```

## 表驱动测试模板

```go
func TestParseSheetName(t *testing.T) {
    tests := []struct {
        name      string
        input     string
        wantZh    string
        wantEn    string
        wantValid bool
    }{
        {"标准格式", "武将|Hero", "武将", "Hero", true},
        {"无分隔符", "Hero", "", "", false},
        {"英文为空", "武将|", "", "", false},
        {"中文为空", "|English", "", "", false},
        {"空字符串", "", "", "", false},
        {"多个分隔符", "武将|Hero|Extra", "", "", false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            zh, en, valid := ParseSheetName(tt.input)
            assert.Equal(t, tt.wantZh, zh)
            assert.Equal(t, tt.wantEn, en)
            assert.Equal(t, tt.wantValid, valid)
        })
    }
}
```

## 集成测试模板

```go
//go:build integration

package check_manager

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

// TestIntegration_CheckWithFilter 集成测试：验证带过滤的检查流程
func TestIntegration_CheckWithFilter(t *testing.T) {
    // 使用真实文件进行集成测试
    excelPath := "tests/resources/"
    casePath := "tests/resources/rules/"

    res, err := CheckWithFilter(excelPath, casePath, []string{"Activity_活动表.xlsx"})

    assert.NoError(t, err)
    assert.NotNil(t, res)
}
```

**运行方式**：`go test ./... -v -tags=integration`

## 回归测试模板

```go
// TestRegression_<BugDescription> 测试"<bug描述>"bug的回归
// 问题：<详细问题描述，包括触发条件、影响范围>
// 修复：<修复方案摘要，如"增加空值检查"、"修正排序逻辑">
func TestRegression_PathMismatch(t *testing.T) {
    // 构造触发原始 bug 的条件
    // ...

    // 验证 bug 已修复
    assert.Equal(t, expected, actual, "路径匹配结果应正确")
}

// TestRegression_DuplicateNotification 测试重复发送通知的bug回归
// 问题：当同一个文件被多次检查时，飞书通知会重复发送
// 修复：在发送前增加去重逻辑
func TestRegression_DuplicateNotification(t *testing.T) {
    notifications := []Notification{
        {Title: "测试", Content: "内容"},
        {Title: "测试", Content: "内容"}, // 重复
    }

    result := Deduplicate(notifications)

    assert.Len(t, result, 1, "应去重为1条通知")
}
```

## 规则测试模板

Excel 检查规则的测试必须覆盖 4 类场景：

```go
package column_check

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

// 构造测试辅助数据
func fakeDataMyRule() (cols [][]string, cIdx int, c1idx int, params map[string]string, sheetMap map[string]interface{}) {
    // cols: 按列存储的二维数组
    // 索引 0-1: 固定行（前两行）
    // 索引 2: 列名行（MJS_FIXED_ROWS_NAME）
    // 索引 3: 类型行
    // 索引 4+: 数据行（MJS_FIXED_ROWS_NUM 起）
    cols = [][]string{
        {"", "", "Id", "int", "1", "2", "3"},
        {"", "", "Value", "string", "正常值", "", "特殊值"},
    }
    cIdx = 1   // Value 列的索引
    c1idx = 0  // Id 列的索引
    params = map[string]string{"min": "1", "max": "100"}
    return
}

func TestMyRule_ShouldPass(t *testing.T) {
    cols, cIdx, c1idx, params, sheetMap := fakeDataMyRule()
    rule := new(MyRule)

    result := rule.Check("", cols, cIdx, c1idx, params, sheetMap)

    assert.Empty(t, result, "正常数据不应报错")
}

func TestMyRule_ShouldFail(t *testing.T) {
    // 构造违规数据
    cols, cIdx, c1idx, params, sheetMap := fakeDataMyRule()
    // 修改数据使其违反规则
    cols[cIdx][4] = "超范围值"
    rule := new(MyRule)

    result := rule.Check("", cols, cIdx, c1idx, params, sheetMap)

    assert.NotEmpty(t, result, "违规数据应报错")
    // 验证错误类型和消息
    assert.Equal(t, "ERROR", result[0].Level)
}

func TestMyRule_ShouldWarn(t *testing.T) {
    // 构造应触发警告的数据
    // ...
}

func TestMyRule_MissingColumn(t *testing.T) {
    // 边界条件：缺少目标列
    cols := [][]string{{"", "", "Id", "int", "1"}}
    rule := new(MyRule)

    // 验证不会 panic
    result := rule.Check("", cols, -1, 0, nil, nil)
    assert.Empty(t, result, "缺少列应优雅处理")
}
```

## 机器人测试模板

### 测试入口（xcard_case_test 目录）

```go
package xcard_case_test

import (
    "context"
    "testing"
    "rain-robot/project/xcard/env"
    "rain-robot/project/xcard/vars"
    "rain-robot/rain_init"
    "rain-robot/robot"
)

func TestMyFeatureCase(t *testing.T) {
    vars.UseOLAP = false
    vars.ServerIp = "127.0.0.1"
    vars.ServerPort = "9999"
    vars.CaseName = "MyFeatureCase"
    vars.BotPrefix = "test"
    vars.LoginTime = 1
    vars.BotNum = 1

    rain_init.RainInit("../xcard_excel/resources", 6060, 1)
    xcard_client.NewClientsRunSync(env.NewEmptyEnvVars(), context.Background())
}
```

### 用例实现（xcard_case 目录）

```go
package xcard_case

import (
    "context"
    "time"
    "rain-robot/robot"
    pb "rain-robot/project/xcard/xcard_pb"
)

type MyFeatureCase struct{}

func (tc *MyFeatureCase) Logic(c robot.Robot, envSnapshot *env.EnvVars, ctx context.Context, cancel context.CancelFunc) {
    // 1. 注册消息处理器
    c.RegisterSyncHandler(func(c robot.Robot, msg interface{}) {
        ack := msg.(*pb.SomeActionAck)
        // 处理响应
    }, new(pb.SomeActionAck))

    // 2. 登录
    err := LoginModule(c, true, 60*time.Second, "0.8.3001.1.1", vars.SameRoleName, ctx, cancel)
    if err != nil {
        return
    }

    // 3. 发送测试请求
    c.Send(&pb.SomeActionReq{...})

    // 4. 等待响应（通过 handler 中的逻辑验证）
    time.Sleep(2 * time.Second)
}
```

### 注册用例（cases.go）

```go
p.RegCase("MyFeatureCase", MyFeatureCase{})
```

## 回归测试检查清单

生成回归测试后，逐项确认：

- [ ] 测试名称以 `TestRegression_` 开头
- [ ] 注释中说明原始 bug（问题）和修复方案（修复）
- [ ] 测试能精确触发原始 bug 的条件
- [ ] 断言验证了修复效果（不只是"不 panic"）
- [ ] 包含边界条件测试（空值、极端值、特殊字符）
- [ ] 使用 `testify/assert` 而非 `t.Log` / `t.Errorf`
- [ ] 测试独立运行，不依赖其他测试的执行顺序
- [ ] 测试可在 CI 环境中运行（不依赖本地资源）
