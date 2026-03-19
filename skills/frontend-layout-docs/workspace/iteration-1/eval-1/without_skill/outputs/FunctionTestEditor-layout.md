# FunctionTestEditor 页面布局文档

## 概述

FunctionTestEditor 是一个功能测试用例编辑器页面，用于配置和管理测试用例。该页面采用经典的"顶部导航 + 左侧树形菜单 + 右侧内容区 + 底部状态栏"的布局结构。

## 整体布局结构

```
+------------------------------------------------------------------+
|                         Header (34px)                            |
|                      [水平菜单导航栏]                              |
+----------+-------------------------------------------------------+
|          |                                                        |
|  Sider   |                    Content                             |
| (240px)  |                  [Tab 内容区]                           |
|          |                                                        |
| [树形    |                                                        |
|  菜单]   |                                                        |
|          |                                                        |
+----------+-------------------------------------------------------+
|                        Footer (64px)                              |
|                   [用例统计信息 + 执行状态]                         |
+------------------------------------------------------------------+
```

## 布局组件详解

### 1. 顶层容器 (n-layout)

- **位置**: `absolute` 定位，占满整个父容器
- **背景色**: `#2b2b2b` (深灰色主题)
- **文字颜色**: 白色

### 2. Header 区域

| 属性 | 值 |
|------|-----|
| 高度 | 34px |
| 布局 | `display: flex; align-items: center` |
| 边框 | `bordered` (底部边框) |
| 组件 | `n-menu` (水平模式) |

**菜单配置**:
- `mode="horizontal"` - 水平导航
- `inverted` - 支持反色模式
- `v-model:value="activeKey"` - 绑定当前激活菜单项

### 3. 主内容区 (n-layout with has-sider)

| 属性 | 值 |
|------|-----|
| 位置 | `absolute; top: 34px; bottom: 64px` |
| 结构 | `has-sider` (包含侧边栏) |

#### 3.1 左侧边栏 (n-layout-sider)

| 属性 | 值 |
|------|-----|
| 宽度 | 240px (展开) / 50px (折叠) |
| 折叠模式 | `collapse-mode="width"` |
| 滚动条 | `native-scrollbar="false"` |
| 触发器 | `show-trigger` (折叠按钮) |
| 边框 | `bordered` |

**侧边栏内容结构**:
```
n-flex (vertical)
├── n-input (搜索框)
├── div (开关容器)
│   ├── n-switch (仅展示过滤/展示全部)
│   └── n-switch (显示描述/隐藏描述)
├── n-tree (树形菜单)
│   - block-line
│   - draggable
│   - checkbox-placement="left"
├── n-dropdown (右键菜单)
└── Modal 组件
    ├── AddCateModal (新增分类)
    ├── AddCaseModal (新增用例)
    ├── RenameCaseModal (重命名用例)
    ├── RenameCateModal (重命名分类)
    └── OptionModal (选项配置)
```

#### 3.2 右侧内容区 (n-flex#Content)

| 属性 | 值 |
|------|-----|
| 宽度 | `100%` |
| 高度 | `100%` |

**Tab 面板结构** (`n-tabs`):
- `size="small"`
- `type="line"`
- `animated` (动画切换)
- `justify-content="space-evenly"`

| Tab 名称 | 组件 | 说明 |
|---------|------|------|
| 用例配置 | InitYanWuPanel | 配置测试用例的初始场景 |
| 用例步骤 | StepsPanel | 配置测试步骤和断言 |
| 执行日志 | RobotTestLog | 显示测试执行日志 |

### 4. Footer 区域

| 属性 | 值 |
|------|-----|
| 高度 | 64px |
| 位置 | `absolute` |
| 内边距 | `0 20px` |
| 布局 | `display: flex; align-items: center; gap: 20px` |

**Footer 内容**:
- `n-statistic` - 用例数量统计 (`n-number-animation`)
- `n-statistic` - 动作数量统计 (`n-number-animation`)
- `FooterCaseLogStatistic` - 执行状态统计组件

## 子组件布局

### InitYanWuPanel (用例配置)

**功能**: 配置测试用例的初始场景，包括武将、手牌、装备等

**布局结构**:
```
n-card (用例标题 + 描述)
├── 负责人输入框
├── n-card (牌堆配置)
│   ├── 牌堆组配置
│   ├── 摸牌堆选择 (n-select multiple)
│   └── 弃牌堆选择 (disabled)
└── VueDraggable (武将列表)
    └── n-card (座位配置) x N
        ├── 人物/技能选择
        ├── 初始手牌
        ├── 初始装备
        ├── 触发装备
        ├── 初始卜卦
        ├── 删除技能
        ├── 增加技能
        └── 技能牌区
```

**关键样式**:
- 武将卡片支持拖拽排序
- 各配置项支持顺序调整开关

### StepsPanel (用例步骤)

**功能**: 配置测试步骤和断言

**布局结构**:
```
VueDraggable (步骤列表)
└── n-card (动作卡片) x N
    ├── header-extra
    │   ├── 拖动按钮
    │   ├── 应用智能描述按钮
    │   ├── 描述输入框
    │   └── 复制按钮
    └── 内容区
        ├── 动作配置行
        │   ├── 动作类型选择
        │   ├── 座位选择
        │   ├── 时间/目标/卡牌等配置
        │   └── 超时时间
        ├── 断言列表 (VueDraggable)
        │   └── n-card (断言卡片) x N
        └── 操作按钮
            ├── 新增断言
            └── 新增动作
```

**动作类型**:
- Sleep (等待)
- PlayCard (出牌)
- DisCard (弃牌)
- OptRoomAction (房间操作)
- UseHeroSkill (使用技能)
- PlayCardOver (结束打牌)
- OnlyAsset (仅断言)

### RobotTestLog (执行日志)

**功能**: 显示测试执行过程中的日志

**布局结构**:
```
n-tabs (type="bar")
└── n-tab-pane (按用例分组)
    └── n-scrollbar
        └── 日志列表
            ├── 时间戳
            ├── 消息ID
            ├── 用例名
            ├── 机器人名
            ├── 日志级别
            └── 消息内容
```

**日志颜色编码**:
- 红色 (`#ff4141`): 断言错误
- 黄色 (`#ffc74d`): 断言警告
- 绿色 (`#66ff5c`): 断言成功
- 紫色 (`#be5cff`): 一般错误

### FooterCaseLogStatistic (执行状态统计)

**布局**:
- 进度条 (`n-progress`) - 显示当前执行进度
- 当前运行用例名称
- 断言错误数目

## 交互功能

### 树形菜单交互

1. **搜索过滤**: 通过 `pattern` 输入框过滤树节点
2. **显示控制**:
   - `showIrrelevantNodes`: 切换仅展示过滤结果/展示全部
   - `showCasesDesc`: 切换显示/隐藏用例描述
3. **拖拽排序**: 支持拖拽调整用例/分类顺序
4. **右键菜单**: 右键点击显示操作菜单

### Tab 面板交互

- **用例步骤 Tab**: 包含右侧锚点导航，快速跳转到指定动作
- **执行日志 Tab**: 自动滚动到最新日志

## Naive UI 组件使用清单

| 组件 | 用途 |
|------|------|
| `n-layout` | 页面布局容器 |
| `n-layout-header` | 顶部导航区 |
| `n-layout-sider` | 侧边栏 |
| `n-layout-footer` | 底部状态栏 |
| `n-menu` | 水平导航菜单 |
| `n-tree` | 树形菜单 |
| `n-dropdown` | 右键下拉菜单 |
| `n-tabs` / `n-tab-pane` | 选项卡面板 |
| `n-card` | 卡片容器 |
| `n-input` | 输入框 |
| `n-input-number` | 数字输入框 |
| `n-select` | 下拉选择框 |
| `n-switch` | 开关 |
| `n-button` | 按钮 |
| `n-tag` | 标签 |
| `n-tooltip` | 工具提示 |
| `n-scrollbar` | 滚动条 |
| `n-anchor` / `n-anchor-link` | 锚点导航 |
| `n-statistic` / `n-number-animation` | 统计数字动画 |
| `n-progress` | 进度条 |
| `n-flex` | 弹性布局 |
| `n-dynamic-tags` | 动态标签 |

## 响应式设计

- 侧边栏支持折叠 (240px -> 50px)
- 内容区自动填充剩余空间
- 步骤配置支持换行 (`flex-wrap: wrap`)

## 文件引用

- **主页面**: `frontend/src/pages/FunctionTestEditor.vue`
- **子组件**:
  - `frontend/src/components/FunctionTest/InitYanWuPanel.vue`
  - `frontend/src/components/FunctionTest/StepsPanel.vue`
  - `frontend/src/components/FunctionTest/RobotTestLog.vue`
  - `frontend/src/components/FunctionTest/FooterCaseLogStatistic.vue`
  - `frontend/src/components/FunctionTest/AddCaseModal.vue`
  - `frontend/src/components/FunctionTest/AddCateModal.vue`
  - `frontend/src/components/FunctionTest/RenameCaseModal.vue`
  - `frontend/src/components/FunctionTest/RenameCateModal.vue`
  - `frontend/src/components/FunctionTest/OptionModal.vue`
