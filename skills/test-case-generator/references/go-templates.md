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

---

## 测试数据构造

### 测试数据工厂模式

当多个测试需要类似但略有不同的数据时，使用工厂函数：

```go
// 工厂函数：创建基础测试数据
func newTestUser(overrides ...func(*User)) *User {
    user := &User{
        ID:    1,
        Name:  "Test User",
        Email: "test@example.com",
        Role:  "user",
    }
    for _, override := range overrides {
        override(user)
    }
    return user
}

// 使用工厂函数
func TestUserPermissions(t *testing.T) {
    // 基础用户
    user := newTestUser()

    // 管理员用户
    admin := newTestUser(func(u *User) {
        u.Role = "admin"
    })

    // 无效邮箱用户
    invalidEmail := newTestUser(func(u *User) {
        u.Email = "invalid"
    })
}
```

### 表驱动测试的数据组织

#### 基本结构

```go
func TestValidateInput(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        wantErr bool
        errMsg  string // 可选：验证特定错误消息
    }{
        {"有效输入", "valid@example.com", false, ""},
        {"空输入", "", true, "不能为空"},
        {"格式错误", "invalid", true, "格式无效"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateInput(tt.input)

            if tt.wantErr {
                require.Error(t, err)
                assert.Contains(t, err.Error(), tt.errMsg)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

#### 嵌套表驱动

当测试需要多个维度的组合时：

```go
func TestPermissionCheck(t *testing.T) {
    tests := []struct {
        name   string
        role   string
        action string
        want   bool
    }{
        // 管理员权限
        {"管理员可读", "admin", "read", true},
        {"管理员可写", "admin", "write", true},
        {"管理员可删", "admin", "delete", true},

        // 普通用户权限
        {"用户可读", "user", "read", true},
        {"用户不可写", "user", "write", false},
        {"用户不可删", "user", "delete", false},

        // 游客权限
        {"游客只读", "guest", "read", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            user := &User{Role: tt.role}
            got := user.Can(tt.action)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### 测试数据文件

对于复杂测试数据，使用外部文件：

```go
// 使用 go:embed 嵌入测试数据
//
//go:embed testdata/valid_user.json
var validUserData string

func TestParseUser(t *testing.T) {
    user, err := ParseUser(validUserData)
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}

// 或从文件读取（适合大文件）
func TestProcessLargeData(t *testing.T) {
    data, err := os.ReadFile("testdata/large_input.json")
    require.NoError(t, err)

    result := Process(data)
    assert.NotNil(t, result)
}
```

### 测试数据可读性

```go
// ❌ 难以理解的魔数
tests := []struct {
    input  int
    want   int
}{
    {100, 1},
    {200, 2},
    {300, 3},
}

// ✅ 清晰的命名和注释
tests := []struct {
    name     string
    score    int
    wantTier int
}{
    {"青铜门槛", 100, 1},  // 100分达到青铜
    {"白银门槛", 200, 2},  // 200分达到白银
    {"黄金门槛", 300, 3},  // 300分达到黄金
}
```

---

## Mock 和依赖注入

### 何时使用 Mock

**需要 Mock 的场景**：
- 外部服务调用（HTTP API、数据库）
- 时间相关（`time.Now()`）
- 随机数生成
- 文件系统操作
- 发送通知/邮件

**不需要 Mock 的场景**：
- 纯逻辑函数（无副作用）
- 简单的数据转换
- 内存中的数据结构操作

### 接口 Mock

```go
// 定义接口
type UserRepository interface {
    FindByID(id int) (*User, error)
    Save(user *User) error
}

// 生产实现
type DBUserRepository struct {
    db *sql.DB
}

// Mock 实现（手动）
type MockUserRepository struct {
    FindByIDFunc func(id int) (*User, error)
    SaveFunc     func(user *User) error
}

func (m *MockUserRepository) FindByID(id int) (*User, error) {
    if m.FindByIDFunc != nil {
        return m.FindByIDFunc(id)
    }
    return nil, errors.New("not implemented")
}

func (m *MockUserRepository) Save(user *User) error {
    if m.SaveFunc != nil {
        return m.SaveFunc(user)
    }
    return errors.New("not implemented")
}

// 使用 Mock
func TestGetUser(t *testing.T) {
    mock := &MockUserRepository{
        FindByIDFunc: func(id int) (*User, error) {
            return &User{ID: id, Name: "Test"}, nil
        },
    }

    service := NewUserService(mock)
    user, err := service.GetUser(1)

    require.NoError(t, err)
    assert.Equal(t, "Test", user.Name)
}
```

### testify/mock 使用

```go
import (
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/assert"
)

// Mock 类型
type MockRepository struct {
    mock.Mock
}

func (m *MockRepository) FindByID(id int) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

// 使用 testify/mock
func TestWithMock(t *testing.T) {
    mockRepo := new(MockRepository)
    mockRepo.On("FindByID", 1).Return(&User{ID: 1, Name: "Alice"}, nil)

    service := NewUserService(mockRepo)
    user, err := service.GetUser(1)

    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    mockRepo.AssertExpectations(t)  // 验证所有期望都被调用
}
```

### Mock 的常见陷阱

#### 陷阱 1：过度 Mock

```go
// ❌ Mock 了不需要 Mock 的东西
func TestAddNumbers(t *testing.T) {
    mockCalc := new(MockCalculator)
    mockCalc.On("Add", 1, 2).Return(3)  // 这只是简单加法！

    // ✅ 直接测试
    assert.Equal(t, 3, Add(1, 2))
}
```

#### 陷阱 2：Mock 行为与真实实现不符

```go
// ❌ Mock 返回了真实数据库不会返回的结果
mockRepo.On("FindByID", -1).Return(&User{}, nil)  // 真实 DB 会返回错误

// ✅ Mock 应反映真实行为
mockRepo.On("FindByID", -1).Return(nil, ErrNotFound)
```

#### 陷阱 3：忘记验证 Mock 期望

```go
func TestWithMock(t *testing.T) {
    mockRepo := new(MockRepository)
    mockRepo.On("FindByID", 1).Return(&User{}, nil)

    service := NewUserService(mockRepo)
    service.GetUser(1)

    // ❌ 缺少验证，无法确认 Mock 是否被调用
}

// ✅ 添加验证
func TestWithMock(t *testing.T) {
    mockRepo := new(MockRepository)
    mockRepo.On("FindByID", 1).Return(&User{}, nil)

    service := NewUserService(mockRepo)
    service.GetUser(1)

    mockRepo.AssertExpectations(t)  // 验证期望
}
```

### 依赖注入模式

```go
// 通过构造函数注入
type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

// 测试时注入 Mock
func TestUserService(t *testing.T) {
    mockRepo := new(MockRepository)
    service := NewUserService(mockRepo)
    // ...
}
```

---

## 测试隔离性

### 原则：每个测试独立

```go
// ❌ 测试间共享状态
var globalCounter int

func TestIncrement(t *testing.T) {
    globalCounter++
    assert.Equal(t, 1, globalCounter)
}

func TestDouble(t *testing.T) {
    // 依赖 TestIncrement 先运行
    globalCounter *= 2
    assert.Equal(t, 2, globalCounter)
}

// ✅ 每个测试独立准备
func TestIncrement(t *testing.T) {
    counter := 0
    counter++
    assert.Equal(t, 1, counter)
}

func TestDouble(t *testing.T) {
    counter := 1  // 独立准备
    counter *= 2
    assert.Equal(t, 2, counter)
}
```

### 使用 t.Parallel() 并行测试

```go
func TestParallel(t *testing.T) {
    // 并行安全的测试可以同时运行
    t.Parallel()

    // 必须使用独立的测试数据
    data := makeTestUser()
    result := Process(data)
    assert.NotNil(t, result)
}
```

### t.Cleanup() 清理资源

```go
func TestWithTempFile(t *testing.T) {
    tmpFile, err := os.CreateTemp("", "test")
    require.NoError(t, err)

    // 注册清理函数
    t.Cleanup(func() {
        os.Remove(tmpFile.Name())
    })

    // 测试代码...
}
```
