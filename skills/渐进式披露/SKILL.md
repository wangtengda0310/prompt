---
name: 使用渐进式披露的风格维护文档
description: 使用渐进式披露的风格进行文档的维护时建议的操作
---

# 使用渐进式披露的风格维护文档

## 建议
使用树状结构维护项目知识
引用代码行号或方法名

## 必须
所有文档可以从CLAUDE.md间接追溯

## 避免
复制代码片段

## 禁止
过长的文档消耗对话token

## 使用示例
树状结构文档
```
CLAUDE.md
doc/CLAUDE-目录结构.md
doc/CLAUDE-概念解释.md
doc/CLAUDE-踩坑记录.md
doc/CLAUDE-功能列表.md
doc/CLAUDE-{具体问题}.md
doc/工作进度.md
doc/回归测试.md

引用代码、文档
```
工作进度参考 doc/工作进度.md 需要实时维护
开发新功能并通过测试后需要维护 doc/回归测试.md
新建工程操作后端代码入口 xxxx.go:行号
新建工程前端界面 xxxx.html
新建工程前端逻辑 xxxx.js中xxxx方法
```