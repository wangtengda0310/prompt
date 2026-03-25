---
name: frontend-layout-docs
description: Generate frontend layout documentation with ASCII diagrams and component tree structures. ALWAYS use this skill when: creating frontend architecture docs, documenting component hierarchies, visualizing page layouts, mapping component dependencies, analyzing nested directory structures (src/pages/*/components/modals), or generating docs to help AI understand frontend codebase structure. Use for Vue, React, and any frontend project needing visual structure documentation.
---

# Frontend Layout Docs Skill

A tool to help AI quickly understand and modify frontend code through layout documentation.

## Use Cases

- New projects needing layout documentation for AI understanding
- Existing projects needing supplementary layout explanations
- Team collaboration requiring unified frontend structure documentation
- AI needing to quickly locate components and modify code

## Core Principle: Three-Layer Structure Consistency

**CRITICAL**: Ensure consistency across three layers of structure:

```
Page Nesting Structure (DOM/Component Hierarchy)
         ↓ should mirror
src Directory Structure (File Organization)
         ↓ should mirror
Documentation Structure (docs/layout/)
```

**Example for function-test page**:

```
src/pages/function-test/
├── index.vue                 # Main page component
├── components/               # Page-specific components
│   ├── modals/              # Nested component directory
│   │   ├── add-case-modal.vue
│   │   └── add-cate-modal.vue
│   ├── init-yanwu-panel.vue
│   └── steps-panel.vue
└── composables/             # Logic layer
    ├── Menu.ts
    └── Tree.ts

docs/layout/pages/function-test/
├── index.md                 # Main page layout doc
├── components.md            # Component tree structure
├── composables.md           # Logic documentation
└── components/
    └── modals.md           # Nested component doc
```

## Document Structure

Generated layout docs **must mirror** the `src/` directory structure:

```
docs/
├── layout/
│   ├── CLAUDE.md              # Index file
│   ├── layouts/               # Layout components (mirrors src/layouts/)
│   │   └── normal-layout.md
│   ├── pages/                 # Page docs (mirrors src/pages/)
│   │   ├── function-test/
│   │   │   ├── index.md       # Main page doc
│   │   │   ├── components.md  # Component hierarchy
│   │   │   ├── composables.md # Logic docs
│   │   │   └── components/
│   │   │       └── modals.md  # Nested components
│   │   ├── hero-wiki-check/
│   │   │   ├── index.md
│   │   │   └── components.md
│   │   └── ...
│   └── shared/                # Shared components (mirrors src/shared/)
│       └── components.md
└── screenshots/               # Optional: screenshots and annotations
    ├── CLAUDE.md
    └── pages/
        └── function-test/
            ├── overview.png
            └── annotations.md
```

## Document Template

### Main Page Document (index.md)

```markdown
# [Page Name] Layout

> File path: `frontend/src/pages/[PageName]/index.vue`
> Route: `/[route]`

## Overview

[Brief description of page functionality]

## ASCII Layout Diagram

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│ [Top Navigation]                                            │ ← Header
├────────────────┬────────────────────────────────────────────┤
│                │ ┌────────────────────────────────────────┐ │
│   Left Sidebar │ │ Tab: [Tab1] [Tab2] [Tab3]             │ │
│   (Sider)      │ └────────────────────────────────────────┘ │
│                │ ┌────────────────────────────────────────┐ │
│   - Menu 1     │ │                                        │ │
│   - Menu 2     │ │         Tab Content Area               │ │
│   - ...        │ │                                        │ │
│                │ └────────────────────────────────────────┘ │
├────────────────┴────────────────────────────────────────────┤
│ [Statistics]                                                │ ← Footer
└─────────────────────────────────────────────────────────────┘
\`\`\`

## Component Tree Structure

> Shows the nesting hierarchy of components and their file locations

\`\`\`
pages/function-test/index.vue                    # Main page (n-layout)
├── n-layout-header                              # Top toolbar
│   └── n-menu (horizontal)                      # Menu options
├── n-layout-sider                               # Left sidebar
│   ├── n-input                                 # Search box
│   ├── n-switch (2x)                           # Display toggles
│   └── n-tree                                  # Test case tree
│       └── n-dropdown                          # Right-click menu
├── n-layout-content                            # Main content area
│   └── n-tabs                                  # Tab navigation
│       ├── Tab: 用例配置
│       │   └── components/init-yanwu-panel.vue
│       ├── Tab: 用例步骤
│       │   └── components/steps-panel.vue
│       │       ├── ActionItem (repeated)
│       │       │   └── components/asset-card.vue (断言)
│       │       └── n-anchor (side navigation)
│       └── Tab: 执行日志
│           └── components/robot-test-log.vue
├── n-layout-footer                              # Bottom status bar
│   ├── n-statistic (2x)                        # Case/Step counts
│   └── components/footer-case-log-statistic.vue
└── Modal Components (components/modals/)
    ├── add-cate-modal.vue                      # Add category dialog
    ├── add-case-modal.vue                      # Add case dialog
    ├── rename-case-modal.vue                   # Rename case dialog
    ├── rename-cate-modal.vue                   # Rename category dialog
    └── option-modal.vue                        # Settings dialog
\`\`\`

## Component File Mapping

| Component | File Path | Line | Description |
|-----------|-----------|------|-------------|
| Main Page | pages/function-test/index.vue | 58-280 | n-layout container |
| Search Input | pages/function-test/index.vue | 77 | v-model:pattern |
| Test Case Tree | pages/function-test/index.vue | 97 | :data=dataRef |
| Init Yanwu Panel | components/init-yanwu-panel.vue | - | 初始演武配置 |
| Steps Panel | components/steps-panel.vue | - | 测试步骤编辑 |
| Robot Test Log | components/robot-test-log.vue | - | 执行日志显示 |
| Add Case Modal | components/modals/add-case-modal.vue | - | 添加用例弹窗 |

## Data Flow

\`\`\`
User Action
    │
    ▼
Handler Function
    │
    ▼
State Update
    │
    └──► Component Reactive Update
\`\`\`

## Key State

| State | File | Type | Description |
|-------|------|------|-------------|
| stateName | scripts/State.ts | Ref<Type> | Description |

## Related Files

### Components (components/)
- `components/init-yanwu-panel.vue` - Initial configuration panel
- `components/steps-panel.vue` - Test step editor
- `components/robot-test-log.vue` - Execution log viewer
- `components/modals/` - Modal dialogs (see modals.md)

### Composables (composables/)
- `composables/Menu.ts` - Top menu configuration
- `composables/Tree.ts` - Tree logic (expand/check/drag)
- `composables/TreeSearch.ts` - Search filtering
```

### Component Hierarchy Document (components.md)

```markdown
# [Page Name] - Component Hierarchy

> Parent: [index.md](./index.md)

## Component Dependency Tree

\`\`\`
index.vue (Main Page)
│
├─── Layout Components (Naive UI)
│    ├── n-layout-header
│    ├── n-layout-sider
│    ├── n-layout-content
│    └── n-layout-footer
│
├─── Page-Specific Components (components/)
│    ├── SearchControls
│    │    ├── n-input
│    │    └── n-switch × 2
│    │
│    ├── InitYanWuPanel
│    │    ├── n-form × 8 (seats)
│    │    └── [Dynamic Form Items]
│    │
│    ├── StepsPanel
│    │    ├── n-anchor
│    │    └── ActionItem × N
│    │         └── AssetCard × M
│    │
│    └── RobotTestLog
│         └── n-tabs
│
└─── Modal Components (components/modals/)
     ├── AddCateModal
     ├── AddCaseModal
     ├── RenameCaseModal
     ├── RenameCateModal
     └── OptionModal
\`\`\`

## Component Details

### SearchControls

**Purpose**: Filter and display test case tree

**Location**: `pages/function-test/index.vue:76-95`

**Sub-components**:
- `n-input` - Search box (v-model:pattern)
- `n-switch` - Show filtered/all (v-model:showIrrelevantNodes)
- `n-switch` - Show/hide description (v-model:showCasesDesc)

**State dependencies**:
- `pattern` (TreeSearch.ts)
- `showIrrelevantNodes` (TreeSearch.ts)
- `showCasesDesc` (TreeSearch.ts)

### InitYanWuPanel

**Purpose**: Configure initial test case settings (武将、手牌、装备等)

**Location**: `pages/function-test/components/init-yanwu-panel.vue`

**Sub-components**: None (uses Naive UI form components)

**Props**: N/A

**Emits**: None

### StepsPanel

**Purpose**: Edit test case steps and assertions

**Location**: `pages/function-test/components/steps-panel.vue`

**Sub-components**:
- `n-anchor` - Step navigation (right side)
- `ActionItem` (repeated) - Individual step
  - `AssetCard` (repeated) - Assertion cards

**State dependencies**:
- `nowCaseData` (use-case-data.ts)
- `actionsSelectOption` (StepActionsAndAssetsSelect.ts)

### RobotTestLog

**Purpose**: Display robot execution logs in real-time

**Location**: `pages/function-test/components/robot-test-log.vue`

**Sub-components**: `n-tabs` - Log tabs per test case

**State dependencies**:
- `logCache` (RobotTestLog.ts)
- Event: `robotLog` (subscribed in index.vue:45)

### Modal Components

See [modals.md](./components/modals.md) for detailed modal component documentation.

## Props Flow

```
index.vue (Parent)
    │
    ├──► InitYanWuPanel
    │       └── nowCaseData (ref)
    │
    ├──► StepsPanel
    │       └── nowCaseData (ref)
    │
    └──► RobotTestLog
            └── (Event-driven: robotLog)
```

## Event Flow

```
Component          Event                  Handler
────────────────────────────────────────────────────────
n-tree            @node-click            → nowCaseData update
n-tree            @drop                  → Reorder tree
n-dropdown        @select                → Modal open/close
StepsPanel        @step-add              → Update nowCaseData.actions
AssetCard         @assertion-add         → Update nowCaseData.assertions
```
```

### Nested Components Document (components/modals.md)

```markdown
# Modal Components

> Parent: [components.md](../components.md)

## Overview

All modal components are located in `pages/function-test/components/modals/`.

## Modal Components Tree

```
components/modals/
├── add-cate-modal.vue      # Add category dialog
├── add-case-modal.vue      # Add case dialog
├── rename-case-modal.vue   # Rename case dialog
├── rename-cate-modal.vue   # Rename category dialog
└── option-modal.vue        # Settings/options dialog
```

## Component Details

### AddCateModal

**Purpose**: Add a new category to the test case tree

**Location**: `pages/function-test/components/modals/add-cate-modal.vue`

**Props**:
```typescript
interface Props {
  show: boolean           // Control visibility
  parentKey?: string      // Parent node key (for nested categories)
}
```

**Emits**:
- `update:show` - Close dialog
- `confirm` - Add category (payload: { name: string, parentKey?: string })

**State dependencies**:
- `dataRef` (TreeAndHistory.ts) - Updates tree data

### AddCaseModal

**Purpose**: Add a new test case

**Location**: `pages/function-test/components/modals/add-case-modal.vue`

**Props**:
```typescript
interface Props {
  show: boolean
  categoryKey: string     // Parent category key
}
```

**Emits**:
- `update:show`
- `confirm` - Add case (payload: { name: string, categoryKey: string })

### RenameCaseModal / RenameCateModal

**Purpose**: Rename a case or category

**Location**: `pages/function-test/components/modals/rename-*-modal.vue`

**Props**:
```typescript
interface Props {
  show: boolean
  nodeKey: string         // Node to rename
  currentName: string     // Current name
}
```

**Emits**:
- `update:show`
- `confirm` - Rename (payload: { nodeKey: string, newName: string })

### OptionModal

**Purpose**: Configure test execution options

**Location**: `pages/function-test/components/modals/option-modal.vue`

**Props**:
```typescript
interface Props {
  show: boolean
}
```

**Emits**:
- `update:show`
- `update` - Update options (payload: TestOptions)

## Usage Flow

```
User right-clicks tree node
    │
    ▼
n-dropdown menu shows (TreeDropDown.ts)
    │
    ├──► "添加分类" → showAddCateModal = true → AddCateModal opens
    ├──► "添加用例" → showAddCaseModal = true → AddCaseModal opens
    ├──► "重命名" → showRenameXxxModal = true → RenameModal opens
    └──► "删除" → Direct action (no modal)
```
```

### Composables Document (composables.md)

```markdown
# Composables - Logic Layer

> Parent: [index.md](./index.md)

## Overview

Composables contain the reactive logic and state management for the page.

## Composables Structure

```
composables/
├── Menu.ts                    # Top menu options
├── Tree.ts                    # Tree expand/check/drag/render
├── TreeSearch.ts              # Search filtering
├── TreeDropDown.ts            # Right-click menu
├── TreeAndHistory.ts          # Tree data and history
├── CaseData.ts / use-case-data.ts  # Current case data
├── Modals.ts                  # Modal visibility states
├── Func.ts                    # Load/save/execute functions
├── FooterStatistic.ts         # Footer statistics
├── RobotTestLog.ts            # Log cache management
└── StepActionsAndAssetsSelect.ts  # Step action options
```

## State Management

### Global State (Shared across components)

| State | File | Type | Used By |
|-------|------|------|---------|
| `nowCaseData` | use-case-data.ts | Ref\<CaseData\> | InitYanWuPanel, StepsPanel |
| `dataRef` | TreeAndHistory.ts | Ref\<TreeOption[]\> | n-tree |
| `pattern` | TreeSearch.ts | Ref\<string\> | Search input |
| `showCasesDesc` | TreeSearch.ts | Ref\<boolean\> | Display toggle |
| `showIrrelevantNodes` | TreeSearch.ts | Ref\<boolean\> | Filter toggle |
| `expandedKeysRef` | Tree.ts | Ref\<string[]\> | n-tree |
| `checkedKeysRef` | Tree.ts | Ref\<string[]\> | n-tree |

### Composable Details

#### Menu.ts

**Exports**: `menuOptions`, `activeKey`

**Purpose**: Top toolbar menu configuration

**Actions**:
- 加载用例 → `handleLoad()`
- 保存用例 → Save all cases
- 执行用例 → Execute current case
- 停止用例 → Stop execution
- 设置 → Open `option-modal`

#### Tree.ts

**Exports**: `expandedKeysRef`, `checkedKeysRef`, `nodeProps`, `handleDrop`, etc.

**Purpose**: Tree component interaction logic

**Features**:
- Expand/collapse nodes
- Checkbox selection
- Drag and drop reordering
- Custom node rendering (with icons)

#### TreeSearch.ts

**Exports**: `pattern`, `showCasesDesc`, `showIrrelevantNodes`

**Purpose**: Search and display filtering

**Logic**: Filters `dataRef` based on `pattern` match

#### CaseData.ts / use-case-data.ts

**Exports**: `nowCaseData`

**Purpose**: Current editing case data

**Structure**:
```typescript
interface CaseData {
  name: string
  description?: string
  owner?: string
  initYanWu: InitYanWuConfig
  actions: Action[]
  assertions?: Assertion[]
}
```

## Data Flow Diagrams

### Case Selection Flow

```
User clicks tree node
    │
    ▼
nodeProps.onClick() (Tree.ts)
    │
    ▼
nowCaseData.value = option (use-case-data.ts)
    │
    ├──► InitYanWuPanel reactive update
    ├──► StepsPanel reactive update
    └──► n-anchor reactive update
```

### Step Addition Flow

```
User clicks "新增步骤"
    │
    ▼
StepsPanel handler
    │
    ▼
nowCaseData.value.actions.push(newAction)
    │
    └──► StepsPanel re-renders (v-for)
```

### Log Event Flow

```
Robot execution (Wails backend)
    │
    ▼
Events.Emit('robotLog', ...)
    │
    ▼
Events.On('robotLog') (index.vue:45)
    │
    ▼
insertLogCache() (RobotTestLog.ts)
    │
    └──► RobotTestLog component update
```
```

### Index File Template (CLAUDE.md)

```markdown
# [Project Name] Frontend Layout Documentation Index

## Document List

| Document | Page | Route | Description |
|----------|------|-------|-------------|
| [Normal-layout.md](./Normal-layout.md) | Layout Component | - | Outer layout |

## Tech Stack

- Framework: Vue 3 / React
- UI Library: Naive UI / Ant Design / Element Plus
- Router: Vue Router / React Router
- State: Pinia / Redux / Context

## Common Components

[List common components and their usage]

## Maintenance

Update corresponding layout docs when page layout changes significantly.
```

## Execution Steps

### 0. Analyze Source Directory Structure

**CRITICAL**: First, understand the actual `src/` directory structure to ensure docs mirror it:

```bash
# Analyze the source directory tree
find frontend/src -type d | head -30
find frontend/src -name "*.vue" -o -name "*.tsx" | head -50

# Build a mental map of the structure:
# - pages/
#   - function-test/
#     - components/
#       - modals/          # ← Nested directory!
#     - composables/
#     - index.vue
#   - hero-wiki-check/
#     - components/
#     - index.vue
# - layouts/
#   - normal-layout/
# - shared/
#   - components/
```

**Key questions to answer**:
- What pages exist in `src/pages/`?
- Does each page have nested directories (e.g., `components/modals/`)?
- Are there shared components in `src/shared/` or `src/components/`?
- What's the layout structure (`src/layouts/`)?

### 1. Create Mirror Directory Structure

Create documentation directories that **exactly mirror** the source structure:

```bash
# Create base directories
mkdir -p docs/layout/pages
mkdir -p docs/layout/layouts
mkdir -p docs/layout/shared

# For each page, create matching subdirectories
# Example for function-test:
mkdir -p docs/layout/pages/function-test/components

# If there are nested component directories (e.g., modals):
mkdir -p docs/layout/pages/function-test/components/modals
```

### 2. Read Key Files

For each page, read in this order:
1. **Main page file** (`pages/[name]/index.vue`)
2. **Component files** (recursive in `components/`)
3. **Composables** (`composables/*.ts`)
4. **Related shared components**

### 3. Generate Documents in Order

**Document generation order** (mirrors importance and dependency):

1. **Layout Components** (`docs/layout/layouts/`)
   - e.g., `normal-layout.md` for `src/layouts/normal-layout/`

2. **Main Pages** (`docs/layout/pages/`)
   - For each page: `index.md` (main layout + ASCII diagram)

3. **Component Hierarchies** (`docs/layout/pages/[name]/components.md`)
   - Component tree structure
   - Props and event flow

4. **Nested Components** (e.g., `docs/layout/pages/[name]/components/modals.md`)
   - Only if there are nested subdirectories

5. **Composables Documentation** (`docs/layout/pages/[name]/composables.md`)
   - Logic layer documentation

6. **Index File** (`docs/layout/CLAUDE.md`)
   - Create last, links to all other docs

### 4. Document Structure Checklist

For each page, ensure you generate:

- [ ] `index.md` - Main page layout with ASCII diagram
- [ ] `components.md` - Component hierarchy tree
- [ ] `components/[nested].md` - For nested component directories (if any)
- [ ] `composables.md` - State management and logic

### 5. Update Root CLAUDE.md

Add layout documentation reference in project root CLAUDE.md:

```markdown
## Frontend Layout Documentation

Layout visualization docs mirror the src/ directory structure:

| Path | Document | Description |
|------|----------|-------------|
| layouts/normal-layout | [normal-layout.md](docs/layout/layouts/normal-layout.md) | Main layout |
| pages/function-test | [function-test/index.md](docs/layout/pages/function-test/index.md) | Function test page |
| pages/function-test/components | [components.md](docs/layout/pages/function-test/components.md) | Component hierarchy |
| pages/function-test/components/modals | [modals.md](docs/layout/pages/function-test/components/modals.md) | Modal dialogs |
```

## ASCII Layout Diagram Standards

### Common Layout Patterns

**Three-Section Layout (Header + Sider/Content + Footer)**
```
┌─────────────────────────────────────────────────────────────┐
│ Header (fixed height)                                       │
├────────────────┬────────────────────────────────────────────┤
│                │                                            │
│   Sider        │            Content                         │
│   (fixed width)│            (adaptive)                      │
│                │                                            │
├────────────────┴────────────────────────────────────────────┤
│ Footer (fixed height)                                       │
└─────────────────────────────────────────────────────────────┘
```

**Single Page Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ Header                                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Content (scrollable)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Two-Column Layout with Anchor Navigation**
```
┌──────────────────────────────────────────────┬─────────────┐
│                                              │             │
│              Main Content                    │   Anchor    │
│              (scrollable)                    │   Nav       │
│                                              │   (fixed)   │
│                                              │             │
└──────────────────────────────────────────────┴─────────────┘
```

### Annotation Standards

- Use `←` to mark area names
- Use `(size)` for fixed dimensions
- Use `(adaptive)` for flexible areas
- Use `(scrollable)` for scrollable areas

## Component Mapping Table Standards

| Column | Description |
|--------|-------------|
| Layout Area | Corresponding area in ASCII diagram |
| Component/Element | Specific component name or HTML element |
| File Location | Source file path and line number |
| Function | Brief function description |

## Data Flow Diagram Standards

Use simple ASCII arrow diagrams:

```
User Action → Event Handler → State Update → Component Response
```

Or detailed version:

```
User clicks button
    │
    ▼
handleClick() function
    │
    ▼
Update ref/reactive state
    │
    ├──► ComponentA auto-updates
    │
    └──► ComponentB auto-updates
```

## Screenshot Annotation Standards

### Directory Structure
```
docs/screenshots/
├── CLAUDE.md
└── PageName/
    ├── overview.png      # Overall screenshot
    ├── detail-xxx.png    # Optional: detail screenshots
    └── annotations.md    # Annotation description
```

### Annotation Document Content

1. **Coordinate Reference Diagram** - Show area divisions
2. **Area Annotation Table** - Location, component, interaction description
3. **Component Details** - Detailed layout of key areas
4. **Interaction Description** - User operation description

## Notes

1. **Keep it concise** - Documentation should help understanding, not be verbose
2. **Reference code** - Use file paths and line numbers rather than copying code
3. **Focus on data flow** - How state flows between components is most important
4. **Mark dimensions** - Clearly distinguish fixed and flexible areas
5. **Index file** - Use CLAUDE.md instead of README.md for AI recognition
6. **Mirror source structure** - Documentation directories must mirror src/ structure

## Component Tree Structure Standards

### Tree Visualization Format

Use indented tree structure with pipe characters to show component hierarchy:

```
ParentComponent
├── ChildComponent1
│   ├── GrandChild1
│   └── GrandChild2
└── ChildComponent2
    ├── GrandChild3
    └── GrandChild4
```

### Tree Node Format

Each node should include:
- **Component name** (PascalCase for custom components, lowercase for library components)
- **File path** (relative to src/)
- **Line number** (if applicable)
- **Brief description** (in parentheses, if needed)

Example:
```
index.vue (Main Page)
├── n-layout-header → index.vue:61
├── n-layout-sider → index.vue:66
│   ├── n-input (Search) → index.vue:77
│   └── n-tree → index.vue:97
└── InitYanWuPanel → components/init-yanwu-panel.vue
```

### Nested Directory Representation

When components are in nested subdirectories (e.g., `components/modals/`), show this clearly:

```
components/modals/              # Directory grouping
├── add-cate-modal.vue
├── add-case-modal.vue
└── rename-case-modal.vue
```

Or as a subtree:
```
Modal Components (components/modals/)
├── AddCateModal
├── AddCaseModal
└── RenameCaseModal
```

### Props and Event Flow in Trees

For complex component relationships, add annotations:

```
ParentComponent
├── ChildComponent (props: data, onAction)
│   └── GrandChild (emits: update)
└── SiblingComponent (shares: dataRef)
```

### Full Example: Component Tree

```
pages/function-test/index.vue                    # Main page container
├── n-layout-header → index.vue:61              # Top toolbar
│   └── n-menu (horizontal) → index.vue:62      # Menu options
├── n-layout-sider → index.vue:66               # Left sidebar (240px)
│   ├── n-input → index.vue:77                  # Search box
│   ├── n-switch (2x) → index.vue:79,87         # Display toggles
│   └── n-tree → index.vue:97                   # Test case tree
│       └── n-dropdown → index.vue:116          # Right-click menu
├── n-layout-content → index.vue:134            # Main content
│   └── n-tabs → index.vue:134                  # Tab panel
│       ├── Tab: 用例配置
│       │   └── InitYanWuPanel → components/init-yanwu-panel.vue
│       ├── Tab: 用例步骤
│       │   └── StepsPanel → components/steps-panel.vue
│       │       ├── ActionItem (v-for)          # Repeated per step
│       │       │   └── AssetCard (v-for)       # Assertion cards
│       │       └── n-anchor → StepsPanel.vue   # Side navigation
│       └── Tab: 执行日志
│           └── RobotTestLog → components/robot-test-log.vue
├── n-layout-footer → index.vue:172             # Bottom status (64px)
│   ├── n-statistic (2x) → index.vue:174,180    # Case/Step counts
│   └── FooterCaseLogStatistic → components/footer-case-log-statistic.vue
└── Modal Components → components/modals/       # Dialog components
    ├── AddCateModal → modals/add-cate-modal.vue
    ├── AddCaseModal → modals/add-case-modal.vue
    ├── RenameCaseModal → modals/rename-case-modal.vue
    ├── RenameCateModal → modals/rename-cate-modal.vue
    └── OptionModal → modals/option-modal.vue
```

### ASCII Art Integration

Combine the tree structure with ASCII layout diagrams for clarity:

**Component Tree**:
```
index.vue
├── Header (n-layout-header)
├── Sider (n-layout-sider)
│   └── Tree (n-tree)
├── Content (n-layout-content)
│   └── Tabs (n-tabs)
└── Footer (n-layout-footer)
```

**ASCII Layout** (shows visual arrangement):
```
┌─────────────────────────────────────────┐
│ Header                                  │
├───────────┬─────────────────────────────┤
│ Sider     │ Content                     │
│           │  ┌─────┬─────┬─────┐       │
│           │  │Tab1 │Tab2 │Tab3 │       │
│           │  └─────┴─────┴─────┘       │
├───────────┴─────────────────────────────┤
│ Footer                                  │
└─────────────────────────────────────────┘
```

Both formats should complement each other and reference the same components.
