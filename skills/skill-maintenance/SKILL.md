---
name: skill-maintenance
description: 全面审计Claude Code skill生态系统，识别冲突、过时文档和维护需求
---

## 触发条件

- 用户要求审计skill系统
- 用户说"检查skills"、"skill维护"、"审计技能"
- 定期维护（建议每周一次）

## 执行步骤

1. 列出所有skill：
```bash
ls -la ~/.claude/skills/
```

2. 分析每个skill的触发条件，识别冲突：
   - 两个skill匹配相同用户输入
   - 触发条件过于宽泛
   - 触发条件过于狭窄导致漏触发

3. 检查CLAUDE.md：
   - 路径是否仍然有效
   - 分支名称是否最新
   - 工作流规则是否过时

4. 验证skill完整性：
   - 是否有对应的测试用例
   - 文档是否完整
   - 是否有重复实现

5. 输出维护报告：
   - 高优先级：冲突skill、过时规则
   - 中优先级：缺少测试、文档不完整
   - 低优先级：优化建议

## 快捷用法

用户可以直接说"/skill-maintenance"或"运行skill维护审计"触发此skill。
