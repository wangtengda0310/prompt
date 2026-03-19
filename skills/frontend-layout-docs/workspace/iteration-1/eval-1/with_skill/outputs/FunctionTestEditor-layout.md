# FunctionTestEditor 页面布局

> 文件路径: `frontend/src/pages/FunctionTestEditor.vue`
> 路由: 功能测试编辑器页面

## 概述

功能测试用例编辑器页面，用于配置、编辑和执行测试用例。页面采用经典的 Header-Sider-Content-Footer 四段式布局，左侧为用例树形导航，右侧为 Tab 页签式内容区，支持用例配置、步骤编辑和执行日志查看。

## ASCII 布局图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [加载用例] [保存用例] [执行用例] [停止用例] [设置] [其他选项▼]              │ ← Header (34px)
├────────────────┬────────────────────────────────────────────────────────────┤
│ [搜索框]       │ ┌────────────────────────────────────────────────────────┐ │
│ [展示全部/仅过滤]│ │ [用例配置] [用例步骤] [执行日志]                       │ │ ← Tab栏
│ [显示描述/隐藏] │ └────────────────────────────────────────────────────────┘ │
│                │ ┌────────────────────────────────────────────────────────┐ │
│   用例树       │ │                                                        │ │
│   (Tree)       │ │                   Tab 内容区                           │ │
│                │ │                   (可滚动)                              │ │
│   ├─ 分类1 (3) │ │                                                        │ │
│   │  ├─ 用例A  │ │                                                        │ │
│   │  └─ 用例B  │ │                                                        │ │
│   └─ 分类2     │ └────────────────────────────────────────────────────────┘ │
│                │                                                            │
│ [右键菜单]      │                                                            │
├────────────────┴────────────────────────────────────────────────────────────┤
│ [XX 条用例] [XX 个动作] [进度条] [当前运行用例] [断言错误数目]              │ ← Footer (64px)
└─────────────────────────────────────────────────────────────────────────────┘
```

## 布局尺寸

| 区域 | 尺寸 |
|------|------|
| Header | 高度 34px |
| Footer | 高度 64px |
| 左侧 Sider | 宽度 240px (可折叠至 50px) |
| 内容区 | 自适应 |

## 组件映射

### 主体结构

| 布局区域 | 组件/元素 | 文件位置 |
|---------|----------|---------|
| Header | n-layout-header | FunctionTestEditor.vue:61 |
| 顶部菜单 | n-menu (horizontal) | FunctionTestEditor.vue:62 |
| 左侧边栏 | n-layout-sider | FunctionTestEditor.vue:66 |
| 内容区 | n-tabs | FunctionTestEditor.vue:134 |
| Footer | n-layout-footer | FunctionTestEditor.vue:172 |

### 左侧边栏组件

| 组件 | 文件位置 | 功能 |
|------|---------|------|
| 搜索框 | n-input | FunctionTestEditor.vue:77 | 用例搜索过滤 |
| 展示开关 | n-switch | FunctionTestEditor.vue:79 | 切换仅展示过滤/展示全部 |
| 描述开关 | n-switch | FunctionTestEditor.vue:87 | 切换显示/隐藏描述 |
| 用例树 | n-tree | FunctionTestEditor.vue:97 | 分类和用例的树形结构 |
| 右键菜单 | n-dropdown | FunctionTestEditor.vue:116 | 分类/用例操作菜单 |
| AddCateModal | components/FunctionTest/AddCateModal.vue | 添加分类弹窗 |
| AddCaseModal | components/FunctionTest/AddCaseModal.vue | 添加用例弹窗 |
| RenameCaseModal | components/FunctionTest/RenameCaseModal.vue | 重命名用例弹窗 |
| RenameCateModal | components/FunctionTest/RenameCateModal.vue | 重命名分类弹窗 |
| OptionModal | components/FunctionTest/OptionModal.vue | 设置弹窗 |

### Tab 内容区组件

| Tab | 组件 | 文件位置 | 功能 |
|-----|------|---------|------|
| 用例配置 | InitYanWuPanel | components/FunctionTest/InitYanWuPanel.vue | 初始演武配置 |
| 用例步骤 | StepsPanel | components/FunctionTest/StepsPanel.vue | 测试步骤编辑 |
| 执行日志 | RobotTestLog | components/FunctionTest/RobotTestLog.vue | 机器人执行日志 |
| 锚点导航 | n-anchor | FunctionTestEditor.vue:147 | 步骤快速跳转 (仅用例步骤Tab) |

### Footer 组件

| 组件 | 文件位置 | 功能 |
|------|---------|------|
| 用例统计 | n-statistic | FunctionTestEditor.vue:174 | 显示用例总数 |
| 动作统计 | n-statistic | FunctionTestEditor.vue:180 | 显示动作总数 |
| FooterCaseLogStatistic | components/FunctionTest/FooterCaseLogStatistic.vue | 运行状态统计 |

## 数据流

```
用户点击树节点
    │
    ▼
nodeProps.onClick() (Tree.ts:171)
    │
    ▼
nowCaseData.value = option (CaseData.ts:8)
    │
    ├──► InitYanWuPanel 组件更新 (显示用例配置)
    │
    ├──► StepsPanel 组件更新 (显示用例步骤)
    │
    └──► n-anchor 组件更新 (锚点导航)
```

```
用户右键树节点
    │
    ▼
nodeProps.onContextmenu() (Tree.ts:181)
    │
    ▼
显示 n-dropdown 菜单
    │
    ▼
handleSelect() 处理菜单选择
    │
    ├──► 添加分类 → showAddCateModal
    ├──► 添加用例 → showAddCaseModal
    ├──► 重命名 → showModifyXxxModal
    └──► 删除 → JsonCaseService.DeleteJSONFile
```

```
执行用例
    │
    ▼
Events.On('robotLog') 订阅事件 (FunctionTestEditor.vue:45)
    │
    ▼
insertLogCache() 写入日志缓存 (RobotTestLog.ts)
    │
    └──► RobotTestLog 组件自动更新显示
```

## 关键状态

| 状态 | 文件 | 类型 | 说明 |
|------|------|------|------|
| nowCaseData | scripts/FunctionTest/CaseData.ts | Ref\<TreeOption & ExtraCaseTreeOption\> | 当前选中/编辑的用例 |
| dataRef | scripts/FunctionTest/TreeAndHistory.ts | Ref\<TreeOption[]\> | 用例树数据 |
| activeKey | scripts/FunctionTest/Menu.ts | Ref\<string \| null\> | 顶部菜单选中项 |
| expandedKeysRef | scripts/FunctionTest/Tree.ts | Ref\<string[]\> | 树展开节点 |
| checkedKeysRef | scripts/FunctionTest/Tree.ts | Ref\<string[]\> | 树勾选节点 |
| pattern | scripts/FunctionTest/TreeSearch.ts | Ref\<string\> | 搜索关键词 |
| showCasesDesc | scripts/FunctionTest/TreeSearch.ts | Ref\<boolean\> | 是否显示用例描述 |
| showIrrelevantNodes | scripts/FunctionTest/TreeSearch.ts | Ref\<boolean\> | 是否显示不相关节点 |
| footerStatisticCaseNum | scripts/FunctionTest/FooterStatistic.ts | ComputedRef\<number\> | 用例总数统计 |
| footerStatisticStepNum | scripts/FunctionTest/FooterStatistic.ts | ComputedRef\<number\> | 动作总数统计 |

## 交互说明

| 操作 | 触发 | 说明 |
|------|------|------|
| 点击用例树节点 | onClick | 加载用例数据到右侧编辑区 |
| 右键分类节点 | onContextmenu | 显示分类操作菜单(添加/重命名/删除等) |
| 右键用例节点 | onContextmenu | 显示用例操作菜单(添加/复制/删除等) |
| 拖拽树节点 | @drop | 调整用例顺序或移动到其他分类 |
| 点击加载用例 | menuOptions.onClick | 从工作目录加载用例 |
| 点击保存用例 | menuOptions.onClick | 保存当前所有用例 |
| 点击执行用例 | menuOptions.onClick | 执行当前选中用例 |
| 点击停止用例 | menuOptions.onClick | 停止正在运行的用例 |
| 搜索框输入 | v-model | 过滤用例树 |
| Tab切换 | n-tabs | 切换编辑视图(配置/步骤/日志) |

## 关联文件

### 脚本文件
- `scripts/FunctionTest/Menu.ts` - 顶部菜单配置
- `scripts/FunctionTest/Tree.ts` - 用例树逻辑(展开/勾选/拖拽/渲染)
- `scripts/FunctionTest/TreeSearch.ts` - 树搜索过滤
- `scripts/FunctionTest/TreeDropDown.ts` - 右键菜单逻辑
- `scripts/FunctionTest/TreeAndHistory.ts` - 树数据和操作历史
- `scripts/FunctionTest/CaseData.ts` - 当前用例数据
- `scripts/FunctionTest/Modals.ts` - 弹窗状态控制
- `scripts/FunctionTest/Func.ts` - 加载/保存/执行用例
- `scripts/FunctionTest/FooterStatistic.ts` - 底部统计数据
- `scripts/FunctionTest/RobotTestLog.ts` - 机器人日志缓存
- `scripts/FunctionTest/StepActionsAndAssetsSelect.ts` - 步骤动作和资产选择

### 组件文件
- `components/FunctionTest/InitYanWuPanel.vue` - 初始演武配置面板
- `components/FunctionTest/StepsPanel.vue` - 测试步骤编辑面板
- `components/FunctionTest/RobotTestLog.vue` - 执行日志面板
- `components/FunctionTest/FooterCaseLogStatistic.vue` - 底部运行状态统计
- `components/FunctionTest/AddCateModal.vue` - 添加分类弹窗
- `components/FunctionTest/AddCaseModal.vue` - 添加用例弹窗
- `components/FunctionTest/RenameCaseModal.vue` - 重命名用例弹窗
- `components/FunctionTest/RenameCateModal.vue` - 重命名分类弹窗
- `components/FunctionTest/OptionModal.vue` - 设置弹窗
- `components/FunctionTest/AssetCard.vue` - 断言卡片组件

## 子页面布局

### 用例配置 Tab (InitYanWuPanel)

```
┌─────────────────────────────────────────────────────────────────┐
│ 用例名称                                    [用例描述输入框]    │
├─────────────────────────────────────────────────────────────────┤
│ 负责人: [输入框]                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 牌堆组: [数字输入]                                               │
│ 摸牌堆: [多选下拉] [顺序调整开关]                                │
│ 弃牌堆: [多选下拉] (禁用)                                        │
├─────────────────────────────────────────────────────────────────┤
│ 座位 1                                    [拖动] [×]            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [武将选择] [身份选择] [势力选择]  初始技能: xxx              │ │
│ │ 初始手牌: [多选下拉] [顺序调整开关]                          │ │
│ │ 初始装备: [多选下拉] [顺序调整开关]                          │ │
│ │ 触发装备: [多选下拉] [顺序调整开关]                          │ │
│ │ 初始卜卦: [多选下拉] [顺序调整开关]                          │ │
│ │ 删除技能: [多选下拉] [顺序调整开关]                          │ │
│ │ 增加技能: [下拉选择] [已选技能标签...]                       │ │
│ │ 技能牌区: [下拉选择] [已选技能标签...]                       │ │
│ │   └─ xxx牌区: [多选下拉]                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ 座位 2 ...                                                      │
│ [增加武将]                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 用例步骤 Tab (StepsPanel)

```
┌──────────────────────────────────────────┬─────────────┐
│ 动作 1               [拖动] [应用智能描述->] [描述输入] [复制] │ ← 锚点导航
│ ┌────────────────────────────────────────────────────────────┐ │   (120px)
│ │ [动作类型] [座位选择] [等待秒数/确认开关/...]              │ │
│ │ [技能选择] [目标选择] [卡牌选择] [当xx牌打出] [超时时间]   │ │
│ ├────────────────────────────────────────────────────────────┤ │
│ │ 断言 1                                    [拖动] [×]       │ │
│ │ [AssetCard 组件]                                          │ │
│ ├────────────────────────────────────────────────────────────┤ │
│ │ [新增断言] [新增]                                          │ │
│ └────────────────────────────────────────────────────────────┘ │
│ 动作 2 ...                                                     │
├──────────────────────────────────────────┴─────────────┘
```

### 执行日志 Tab (RobotTestLog)

```
┌─────────────────────────────────────────────────────────────────┐
│ [用例名1(红色/白色)] [用例名2] ...                              │ ← Tab栏
├─────────────────────────────────────────────────────────────────┤
│ [时间], ID[x], Case[x], name[x], [Level], 消息内容             │
│ [时间], ID[x], Case[x], name[x], [Level], 消息内容             │
│ ...                                                             │
│ (可滚动，自动滚动到底部)                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 特殊说明

1. **用例树节点类型**: 分为 Categories(分类) 和 Cases(用例) 两种 levelType
2. **修改标记**: 被修改的用例/分类会以绿色显示并带有 `*` 前缀
3. **事件订阅**: 页面加载时订阅 `robotLog` 事件，卸载时取消订阅
4. **拖拽排序**: 使用 vue-draggable-plus 实现用例和步骤的拖拽排序
5. **锚点导航**: 用例步骤 Tab 右侧有锚点导航，可快速跳转到指定步骤
