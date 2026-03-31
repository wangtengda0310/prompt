---
name: frontend-layout-docs
description: Generate comprehensive frontend layout documentation with ASCII diagrams, TypeScript interfaces, and component hierarchy analysis. Use this skill when: (1) documenting page layouts or component structures, (2) analyzing component hierarchies and relationships, (3) creating visual layout diagrams for AI understanding, (4) updating existing layout documentation, (5) reviewing code structure for potential issues. Triggers on requests involving "布局文档", "layout", "component hierarchy", "页面结构", "组件层次", or any frontend architecture documentation task.
---

# Frontend Layout Docs Skill

Generate comprehensive layout documentation to help AI quickly understand and modify frontend code.

## Use Cases

- New projects needing layout documentation for AI understanding
- Existing projects needing supplementary layout explanations
- Team collaboration requiring unified frontend structure documentation
- AI needing to quickly locate components and modify code
- Code review: identifying potential issues in component structure

## Document Structure

Generated layout docs are stored in `docs/layout/` directory:

```
docs/
├── layout/
│   ├── CLAUDE.md              # Index file
│   ├── Normal-layout.md       # Layout component
│   └── PageName-layout.md     # Page layout docs
└── screenshots/               # Optional: screenshots and annotations
```

## Document Template

### Single Page Layout Template

```markdown
# [Page Name] Layout

> File path: `frontend/src/pages/[FileName].vue`
> Route: `/[route]`

## Overview

[Brief description of page functionality - what the page does and its purpose]

## ASCII Layout Diagram

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│ [Top Navigation]                                            │ ← Header
├────────────────┬────────────────────────────────────────────┤
│                │ ┌────────────────────────────────────────┐ │
│   Left Sidebar │ │ Tab: [Tab1] [Tab2] [Tab3]             │ │
│   (240px)      │ └────────────────────────────────────────┘ │
│                │ ┌────────────────────────────────────────┐ │
│   - Menu 1     │ │                                        │ │
│   - Menu 2     │ │         Tab Content Area               │ │
│                │ │         (scrollable)                   │ │
│                │ └────────────────────────────────────────┘ │
├────────────────┴────────────────────────────────────────────┤
│ [Statistics]                                                │ ← Footer
└─────────────────────────────────────────────────────────────┘
\`\`\`

## Layout Dimensions

| Area | Size | Notes |
|------|------|-------|
| Header | Height XXpx | Fixed |
| Footer | Height XXpx | Fixed |
| Left Sider | Width XXpx | Collapsible to XXpx |
| Content | Adaptive | Scrollable |

## Component Hierarchy Tree

\`\`\`
PageComponent (index.vue)
├── n-layout (root container)
│   ├── n-layout-header
│   │   └── n-menu (horizontal navigation)
│   │
│   ├── n-layout (has-sider)
│   │   ├── n-layout-sider (left sidebar)
│   │   │   ├── SearchInput
│   │   │   ├── FilterSwitches
│   │   │   └── TreeComponent
│   │   │
│   │   └── n-layout-content
│   │       └── TabContainer
│   │           ├── Tab1: ConfigPanel
│   │           │   └── FormComponents...
│   │           ├── Tab2: StepsPanel
│   │           │   └── DraggableCards...
│   │           └── Tab3: LogPanel
│   │
│   └── n-layout-footer
│       └── StatusBar
\`\`\`

## Component Mapping

### Main Structure

| Layout Area | Component/Element | File Location | Function |
|-------------|-------------------|---------------|----------|
| Root Container | n-layout | Page.vue:10 | Root layout wrapper |
| Header | n-layout-header | Page.vue:15 | Top navigation bar |
| Left Sidebar | n-layout-sider | Page.vue:20 | Side navigation |
| Content | n-layout-content | Page.vue:35 | Main content area |
| Footer | n-layout-footer | Page.vue:50 | Status bar |

### Sub-components

| Component | File Location | Props | Function |
|-----------|---------------|-------|----------|
| ComponentA | components/ComponentA.vue | prop1, prop2 | Description |
| ComponentB | components/ComponentB.vue | - | Description |

## TypeScript Interface Definitions

### Props Interface

\`\`\`typescript
interface PageProps {
  headerTitle?: string      // Header title text
  sideOption?: SideConfig   // Sidebar configuration
}

interface SideConfig {
  title: string
  collapsed?: boolean
}
\`\`\`

### State Interface

\`\`\`typescript
interface PageState {
  loading: Ref<boolean>
  data: Ref<DataType[]>
  selectedItem: Ref<string | null>
}

interface DataType {
  id: string
  name: string
  // ... other fields
}
\`\`\`

### API Response Interface (if applicable)

\`\`\`typescript
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// Example usage
interface UserInfoResponse extends ApiResponse<UserInfo> {}
\`\`\`

## Data Flow Diagram

### Phase 1: User Interaction Flow

\`\`\`
┌──────────────────────────────────────────────────────────────────────────┐
│                          User Interaction Flow                            │
└──────────────────────────────────────────────────────────────────────────┘

User Input                      Component State                Actions
─────────────────────────────────────────────────────────────────────────────

[Input Field] ────────────────> inputValue (ref)
    │                                │
    │ onInput                        │
    ▼                                ▼
handleInput() ────────────────> Validate & Update
    │
    │ [Submit Button]
    ▼
handleSubmit() ───────────────> loading.value = true
    │
    │ API Call
    ▼
Backend Service
\`\`\`

### Phase 2: State Update Flow

\`\`\`
┌──────────────────────────────────────────────────────────────────────────┐
│                          State Update Flow                                │
└──────────────────────────────────────────────────────────────────────────┘

Backend Response
    │
    ▼
Update State (data.value = response.data)
    │
    ├──► ComponentA (auto-reactive update)
    │         │
    │         └──► Re-render with new data
    │
    ├──► ComponentB (computed recalculation)
    │         │
    │         └──► Derived values updated
    │
    └──► ComponentC (watch effect)
              │
              └──► Side effects executed
\`\`\`

### Phase 3: Data Display Flow

\`\`\`
┌──────────────────────────────────────────────────────────────────────────┐
│                          Data Display Flow                                │
└──────────────────────────────────────────────────────────────────────────┘

State (data)
    │
    ├──► List Rendering (v-for)
    │         │
    │         └──► ItemComponent x N
    │                   │
    │                   └──► Display item details
    │
    ├──► Conditional Rendering (v-if)
    │         │
    │         └──► Show/hide based on conditions
    │
    └──► Computed Properties
              │
              └──► Filtered/sorted/transformed data
\`\`\`

## Key State

| State | File | Type | Default | Description |
|-------|------|------|---------|-------------|
| stateName | composables/State.ts | `Ref<Type>` | - | Description |
| computedValue | composables/Computed.ts | `Computed<Type>` | - | Computed from... |

## Backend Services (if applicable)

| Service | Method | Parameters | Return Type | Description |
|---------|--------|------------|-------------|-------------|
| ServiceName | methodName | (param: Type) | Promise<Result> | Description |

## Interactions

| Action | Trigger | Handler | Description |
|--------|---------|---------|-------------|
| Click button | @click="handleClick" | handleClick() | Description |
| Form submit | @submit="onSubmit" | onSubmit() | Description |
| Route change | watch($route) | onRouteChange() | Description |

## External Dependencies

### Shared Components

| Component | Location | Props | Usage |
|-----------|----------|-------|-------|
| SharedComponent | shared/components/ | prop1, prop2 | Description |

### Composables/Hooks

| Composable | Location | Exports | Purpose |
|------------|----------|---------|---------|
| useFeature | composables/useFeature.ts | state, actions | Description |

### Configuration Files

| Config | Location | Purpose |
|--------|----------|---------|
| configName | config/Config.ts | Description |

## Styling Notes

| Selector | Style | Description |
|----------|-------|-------------|
| .className | display: flex; | Layout method |
| #idName | position: fixed; | Positioning |

## Code Review Notes

### Potential Issues

> ⚠️ Document any code issues discovered during analysis

1. **Unused Variables/Functions**: List any defined but unused code
   - Example: `unusedVar` defined at line 20 but never referenced

2. **Inconsistent Patterns**: Note any inconsistent coding patterns
   - Example: Different styling applied to similar components

3. **Performance Concerns**: Identify potential performance issues
   - Example: Large list without virtualization
   - Example: Missing debounce on frequent updates

4. **Accessibility Issues**: Note any accessibility concerns
   - Example: Missing aria labels
   - Example: Insufficient color contrast

5. **Technical Debt**: Note areas that could be improved
   - Example: Commented-out code that should be removed
   - Example: Hard-coded values that should be configurable

### Best Practices Followed

- ✅ Proper TypeScript typing
- ✅ Composables for reusable logic
- ✅ Proper cleanup in onUnmounted

## Related Files

### Component Files
- `components/Xxx.vue` - Description

### Logic Files
- `composables/Xxx.ts` - Description

### Type Definitions
- `@bindings/xxx` - Auto-generated types from backend

---
**Verification Date**: YYYY-MM-DD
**Status**: Document matches / needs update for current code implementation
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
- State: Pinia / Redux / Composables

## Common Components

| Component | Location | Usage |
|-----------|----------|-------|
| SharedComponent | shared/components/ | Description |

## Maintenance

- Update layout docs when page structure changes significantly
- Run verification when dependencies are updated
- Keep TypeScript interfaces in sync with actual code
```

## Execution Steps

### 1. Analyze Project Structure

```bash
# View frontend directory structure
ls frontend/src/

# View page files
ls frontend/src/pages/

# View layout components
ls frontend/src/layout/ 2>/dev/null || ls frontend/src/layouts/ 2>/dev/null

# View router config
cat frontend/src/router/index.ts
```

### 2. Read Key Files

For each page, read:
- Page component file (`.vue` / `.tsx`)
- Related composables (`composables/`, `hooks/`, `stores/`)
- Sub-component files (`components/`)
- Type definitions (`types/`, `@bindings/`)

### 3. Extract TypeScript Interfaces

**IMPORTANT**: Always extract and document TypeScript interfaces:
- Props interfaces from component definition
- State interfaces from composables
- API response interfaces from service calls
- Type imports from `@bindings/` or local type files

### 4. Generate Layout Docs

Create documents in this order:
1. **Layout Component** - Unified layout (e.g., Normal.vue)
2. **Main Pages** - Sorted by importance
3. **Index File** - Create CLAUDE.md last

### 5. Code Review Analysis

During documentation, identify and note:
- Unused variables, functions, or computed properties
- Inconsistent patterns (styling, naming, structure)
- Performance concerns (missing virtualization, excessive re-renders)
- Accessibility issues
- Technical debt (commented code, hard-coded values)

### 6. Update Project CLAUDE.md

Add layout documentation reference in project root CLAUDE.md

## ASCII Layout Diagram Standards

### Common Layout Patterns

**Three-Section Layout (Header + Sider/Content + Footer)**
```
┌─────────────────────────────────────────────────────────────┐
│ Header (fixed height)                                       │
├────────────────┬────────────────────────────────────────────┤
│                │                                            │
│   Sider        │            Content                         │
│   (240px)      │            (adaptive, scrollable)          │
│   collapsible  │                                            │
│                │                                            │
├────────────────┴────────────────────────────────────────────┤
│ Footer (fixed height)                                       │
└─────────────────────────────────────────────────────────────┘
```

**Two-Column Layout with Anchor Navigation**
```
┌──────────────────────────────────────────────┬─────────────┐
│                                              │             │
│              Main Content                    │   Anchor    │
│              (scrollable)                    │   Nav       │
│                                              │   (120px)   │
│                                              │   fixed     │
└──────────────────────────────────────────────┴─────────────┘
```

**Tab-Based Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ [Tab 1] [Tab 2] [Tab 3]                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Tab Content                              │
│                    (changes based on selection)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Annotation Standards

- Use `←` to mark area names
- Use `(size)` for fixed dimensions (e.g., `(240px)`)
- Use `(adaptive)` for flexible areas
- Use `(scrollable)` for scrollable areas
- Use `(collapsible)` for collapsible sections
- Include component names in brackets `[ComponentName]`

## Component Hierarchy Tree Standards

```
PageComponent (filename.vue)
├── LayoutComponent
│   ├── HeaderSection
│   │   └── NavigationMenu
│   │       └── MenuItem x N
│   │
│   └── ContentArea
│       ├── SidebarComponent
│       │   ├── SearchInput
│       │   └── TreeView
│       │
│       └── MainContent
│           └── TabContainer
│               ├── Tab1: PanelA
│               └── Tab2: PanelB
```

## TypeScript Interface Standards

### Naming Conventions

- Props: `ComponentNameProps`
- State: `ComponentNameState` or describe purpose (e.g., `UserFormData`)
- API Response: `ApiResponseType` or `EndpointNameResponse`
- Generic types: Use meaningful names like `TData`, `TItem`

### Required Sections

1. **Props Interface** - All component props with types and descriptions
2. **State Interface** - Reactive state variables
3. **API Response Interface** - Backend data structures (if applicable)

## Data Flow Diagram Standards

### Three-Phase Approach

1. **User Interaction Flow**: How user actions trigger state changes
2. **State Update Flow**: How state changes propagate to components
3. **Data Display Flow**: How data is rendered in the UI

### Diagram Elements

- Use `───►` for direct flow
- Use `├──►` and `└──►` for branching
- Use boxes (`┌─┐`) for grouping related steps
- Label each phase clearly

## Code Review Notes Standards

### Issue Categories

1. **Unused Code**: Variables, functions, computed properties
2. **Inconsistent Patterns**: Styling, naming, structure differences
3. **Performance**: Rendering, memory, network concerns
4. **Accessibility**: ARIA, keyboard nav, contrast
5. **Technical Debt**: TODOs, commented code, hard-coded values

### Format

```markdown
### Potential Issues

1. **Category**: Description
   - Example: `variableName` at line XX - reason
```

## Notes

1. **Keep it concise** - Documentation should help understanding, not be verbose
2. **Reference code** - Use file paths and line numbers rather than copying code
3. **Focus on data flow** - How state flows between components is most important
4. **Mark dimensions** - Clearly distinguish fixed and flexible areas
5. **Include TypeScript types** - Always document interfaces for type safety
6. **Note issues** - Document potential problems discovered during analysis
7. **Use CLAUDE.md** - Use CLAUDE.md instead of README.md for AI recognition
8. **Verify dates** - Include verification date and status in each document
