---
name: skill-ecosystem
description: 多Agent Skill生态系统 — 并行steward agent持续监控、测试和优化skill生态
---

## 触发条件

以下场景触发此skill：
- 用户说"运行skill生态审计"或"/skill-ecosystem"
- 新增/修改skill后需要验证生态健康
- 定期维护（建议每周与/skill-maintenance交替运行）

## Steward Agent架构

### EXCEL_STEWARD

**领域**：excel-parser + snapshot验证 + 配表检查

**职责**：
1. 维护TEST_HARNESS（≥5测试）：
   - 单表查询测试
   - 字段结构解析测试
   - 筛选条件测试
   - Git版本对比测试
   - 测试用Excel生成测试
2. 发布CAPABILITIES：
   - 触发器：单表操作关键词
   - 输入：表名、字段条件、行范围
   - 输出：数据行、字段结构、差异报告
   - 冲突：game-config-analyzer（多表操作）
3. 监控冲突：检测与game-config-analyzer的触发器重叠

### GIT_STEWARD

**领域**：worktree + branch + commit操作

**职责**：
1. 维护TEST_HARNESS（≥5测试）：
   - worktree创建/删除测试
   - 分支验证测试
   - rebase流程测试
   - push安全测试
   - submodule同步测试
2. 发布CAPABILITIES：
   - 触发器：git操作关键词
   - 输入：分支名、commit范围
   - 输出：操作结果、风险评估
   - 冲突：无（但需与CLAUDE.md规则一致）
3. 监控冲突：检测skill与CLAUDE.md规则不一致

### NOTIFY_STEWARD

**领域**：Feishu卡片 + 控制台输出 + 前端面板

**职责**：
1. 维护TEST_HARNESS（≥5测试）：
   - Feishu消息格式测试
   - 控制台输出测试
   - 前端面板更新测试
   - Observer模式测试
   - 错误通知测试
2. 发布CAPABILITIES：
   - 触发器：通知相关关键词
   - 输入：消息内容、目标渠道
   - 输出：发送状态、错误信息
   - 冲突：lark-* skills（飞书操作）
3. 监控冲突：检测与lark-im/lark-doc等skill的触发器重叠

### DOC_STEWARD

**领域**：渐进式披露 + CLAUDE.md规则维护

**职责**：
1. 维护TEST_HARNESS（≥5测试）：
   - 文档层级完整性测试
   - 路径有效性测试
   - 规则一致性测试
   - 新旧文档同步测试
   - 索引更新测试
2. 发布CAPABILITIES：
   - 触发器：文档维护关键词
   - 输入：文件路径、变更内容
   - 输出：更新后的文档结构
   - 冲突：init skill（首次创建CLAUDE.md）
3. 监控冲突：检测与init skill的边界

## CONFLICT_DETECTION协议

### 每日运行

```
1. 收集所有steward的CAPABILITIES清单
2. 比较触发器模式：
   - 完全重叠：两个skill匹配相同输入
   - 部分重叠：一个skill触发器包含另一个
   - 边界模糊：用户输入可能同时匹配多个
3. 比较假设冲突：
   - 技能A假设文件在X位置，技能B假设在Y位置
   - 技能A使用旧分支名，技能B使用新分支名
4. 输出CONFLICT_REPORT
```

### CONFLICT_REPORT格式

```yaml
high_risk:
  - skill_a: excel-parser
    skill_b: game-config-analyzer
    issue: 用户说"查看Hero表数据"可能同时触发两者
    resolution: 明确区分"单表"vs"多表"关键词

medium_risk:
  - skill_a: git-safe
    issue: CLAUDE.md中分支规则与skill描述不一致
    resolution: 同步更新两者

low_risk:
  - skill_a: lark-im
    skill_b: notify-steward
    issue: 都处理飞书消息发送
    resolution: 明确分工（lark-im处理IM操作，notify-steward处理系统通知）
```

## RESOLUTION_PLAN排序

按以下维度排序：
1. **用户影响**：冲突导致多少次错误触发
2. **迁移成本**：修复需要多少文件变更
3. **紧急程度**：是否影响当前开发工作

## 父Agent聚合流程

### 每周运行

```
1. 收集所有steward的周报：
   - 测试通过率
   - 新发现的冲突
   - 提出的优化建议
2. 自主执行低风险优化：
   - 文档更新
   - 测试补充
   - 触发器微调
3. 排队高风险变更：
   - skill合并/拆分
   - 架构调整
   - 新增steward
4. 生成AGGREGATE_REPORT给用户审批
```

## 启动流程

首次运行时，每个steward执行：

```
1. 审计当前领域所有skill
2. 从现有会话记录提取测试场景
3. 创建初始TEST_HARNESS
4. 识别3个最高风险冲突模式
5. 提交INITIAL_AUDIT_REPORT
```

## 禁止

- steward不维护TEST_HARNESS就运行
- 发现冲突不报告就静默处理
- 高风险变更不排队就自主执行
