---
name: go-pkg-refactor
description: |
  Go 项目按领域隔离的目录重构技能。当用户需要重组 Go 项目的包结构、
  按前端页面/功能领域组织后端代码、合并/拆分/移动包、修复 import 路径、
  处理包名冲突时触发此技能。
  适用于：
  - 按领域（前端页面/功能模块）重组 pkg 目录
  - 将代码移动到对应领域目录，减少跨包暴露
  - 合并分散的 MCP 工具到领域统一的 mcp.go
  - 拆分过大的包为 wails.go + mcp.go + services.go
  - 移动/重命名包目录
  - 扁平化嵌套包结构
  - 清理未使用的包或文件
  - 修复因包移动导致的 import 错误
  - 处理同名函数/类型的包内冲突
  即使任务看起来简单，也使用此技能确保不遗漏步骤。
---

# Go 项目按领域隔离的目录重构技能

## 架构目标

按**前端页面/功能领域**组织后端代码，每个领域一个目录，内部文件分工明确：

```
pkg/
├── settings/           # 对应前端 Settings 页面
│   ├── wails.go        # Wails 前端交互方法
│   ├── mcp.go          # MCP 工具注册（暴露业务逻辑）
│   ├── utils.go        # 领域内辅助函数
│   └── home/           # Settings 下的子领域
│       └── wails.go
├── excel-test/         # 对应前端 ExcelTest 页面
│   ├── wails.go        # Wails 方法
│   ├── mcp.go          # MCP 工具
│   └── context.go      # 业务逻辑
├── function-test/      # 对应前端 FunctionTest 页面
│   ├── wails.go
│   ├── mcp.go
│   └── services.go
├── common/             # 跨领域共享（不对应前端页面）
│   ├── game/           # 游戏数据服务
│   ├── mcp/            # MCP 通用工具（TextResult/ErrorResult）
│   └── robotext/       # Robot 扩展
└── types.go            # 跨领域类型定义
```

**核心原则**：
- 每个领域目录尽量**少暴露代码到外界**
- `wails.go` 负责与前端交互（薄层适配器，**不应包含业务逻辑**）
- `mcp.go` 负责将业务逻辑暴露为 MCP 工具（薄层适配器，**不应包含业务逻辑**）
- 业务逻辑集中在 `services.go`、`context.go` 或类似文件中
- 未来可增加 `http.go` 用于调试（同样是薄层适配器）
- `common/` 只放真正跨领域共享的代码

**文件职责边界**：

| 文件 | 职责 | 方法行数限制 |
|------|------|-------------|
| `wails.go` | 接收前端请求 → 调用业务逻辑 → 返回结果 | ≤ 20 行 |
| `mcp.go` | 注册 MCP 工具 → 调用业务逻辑 → 返回结果 | ≤ 20 行 |
| `http.go` | 接收 HTTP 请求 → 调用业务逻辑 → 返回结果 | ≤ 20 行 |
| `services.go` | 核心业务逻辑实现 | 无限制 |
| `context.go` | 领域上下文、状态管理 | 无限制 |
| `utils.go` | 领域内辅助函数 | 无限制 |

> **反模式**：`wails.go` 中出现几十甚至上百行的方法，说明业务逻辑泄露到了适配层。应提取到 `services.go` 中。

## 重构流程

### 阶段一：分析

1. **确定领域划分**
   - 对照前端页面路由，确定后端领域目录
   - 识别哪些代码属于哪个领域
   - 识别哪些代码是跨领域共享的（应放入 `common/`）

2. **列出待移动的文件和目标位置**
   - 确认源目录下的所有文件（包括测试文件、子目录）
   - 确认目标位置是否已存在同名文件

3. **查找所有引用方**
   ```bash
   # 查找 import 引用
   grep -r "pkg/old-path" --include="*.go" .

   # 查找前端 bindings 引用（Wails 项目）
   grep -r "pkg/old-path" --include="*.vue" --include="*.ts" frontend/

   # 查找文档引用
   grep -r "pkg/old-path" --include="*.md" .
   ```

4. **识别潜在冲突**
   - 目标包是否已有同名函数/类型？
   - 移动后是否会导致循环依赖？
   - 包名是否与现有包冲突？

### 阶段二：移动

1. **创建目标目录**
   ```bash
   mkdir -p pkg/new-location
   ```

2. **使用 git mv 移动文件**
   ```bash
   git mv pkg/old-path/file.go pkg/new-location/
   ```
   > 对目录内的每个文件执行，不要直接 mv 整个目录（git 可能无法正确追踪）

3. **移动子目录**
   ```bash
   git mv pkg/old-path/subdir pkg/new-location/
   ```

4. **删除空目录**
   ```bash
   rmdir pkg/old-path  # 确认为空后再删除
   ```

### 阶段三：修复

1. **修改被移动文件的包名**（如果目录名改变导致包名需要改变）
   ```go
   // 旧
   package oldname
   // 新
   package newname
   ```

2. **更新所有 import 路径**
   - Go 文件中的 import
   - 前端 bindings import（Wails 项目）
   - 文档中的路径引用

3. **处理包内冲突**
   - 如果目标包已有同名函数，重命名被移动的函数
   - 如果存在重复实现，删除重复项，保留最完整的版本
   - 如果两个函数都需要保留（参数不同），考虑重命名或合并

4. **编译验证**
   ```bash
   go build ./...
   ```

### 阶段四：清理与验证

1. **检查并删除未使用的文件**
   - 空包目录
   - 无引用的工具函数文件
   - 重复的代码文件

2. **运行测试**
   ```bash
   go test ./pkg/...
   ```

3. **最终验证**
   ```bash
   # 确认无旧路径引用残留
   grep -r "pkg/old-path" --include="*.go" . || echo "无残留"
   ```

## 常见陷阱与处理

### 陷阱 1：同名函数冲突

**症状**：`RegisterGameExcelTools redeclared in this block`

**处理**：
1. 查看两个函数的定义和调用方
2. 如果一个是完整版一个是精简版，保留被调用的版本
3. 如果都无调用方，保留最完整的版本
4. 如果都需要保留，重命名其中一个

### 陷阱 2：前端 bindings 路径失效

**症状**：Wails 构建失败，前端 import 找不到模块

**处理**：
1. 更新前端源码中的 bindings import 路径
2. 路径格式：`@bindings/git.devcloud.ztgame.com/.../pkg/new-path`

### 陷阱 3：循环依赖

**症状**：`import cycle not allowed`

**处理**：
1. 提取公共接口到独立包
2. 或使用接口解耦（让上层包依赖接口而非具体实现）

### 陷阱 4：业务逻辑泄露到适配层

**症状**：`wails.go` 或 `mcp.go` 中出现几十甚至上百行的方法

**处理**：
1. 识别方法中的业务逻辑部分
2. 在 `services.go` 或 `context.go` 中创建新的业务方法
3. 将业务逻辑迁移到新方法
4. `wails.go`/`mcp.go` 中只保留参数解析和结果封装

**示例**：
```go
// 重构前（wails.go 中 80 行的方法）
func (s *Service) HandleComplexOperation(param1, param2 string) (string, error) {
    // 20 行参数校验
    // 30 行业务逻辑
    // 20 行结果组装
    // 10 行错误处理
}

// 重构后
// wails.go（薄层）
func (s *Service) HandleComplexOperation(param1, param2 string) (string, error) {
    result, err := s.logic.ComplexOperation(param1, param2)
    if err != nil {
        return "", err
    }
    return result, nil
}

// services.go（业务逻辑）
func (l *Logic) ComplexOperation(param1, param2 string) (string, error) {
    // 80 行业务逻辑
}
```

### 陷阱 5：git 历史丢失

**症状**：代码审查时显示文件是"新增"而非"移动"

**处理**：
- 使用 `git mv` 而非 `mv`
- 如果已经用了 `mv`，可以 `git add` 后 git 会尝试检测重命名

## 提交策略

建议将重构分为多个提交：

1. `refactor: 将 X 移动到 Y` — 纯移动，无逻辑变更
2. `refactor: 合并 A 和 B` — 合并包并解决冲突
3. `refactor: 删除未使用的 Z` — 清理
4. `fix: 更新前端 bindings 路径` — 前端适配

最后使用 `git rebase -i` squash 为一个提交，或保持分开以便审查。

## 验证清单

- [ ] 所有文件已用 `git mv` 移动
- [ ] 被移动文件的包名已更新
- [ ] 所有 Go import 路径已更新
- [ ] 所有前端 bindings import 已更新
- [ ] 所有文档引用已更新
- [ ] `go build ./...` 通过
- [ ] `go test ./pkg/...` 通过（或确认失败与重构无关）
- [ ] `grep` 确认无旧路径残留
- [ ] 空目录已删除
- [ ] 每个领域目录结构符合规范（wails.go + mcp.go + 业务逻辑）
- [ ] `wails.go` 中所有方法 ≤ 20 行（无业务逻辑泄露）
- [ ] `mcp.go` 中所有方法 ≤ 20 行（无业务逻辑泄露）
