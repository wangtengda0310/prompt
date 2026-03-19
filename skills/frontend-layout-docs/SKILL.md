---
name: frontend-layout-docs
description: Document and visualize frontend page structure and component layouts. Generates ASCII diagrams and component mapping tables. Use when user wants to: document components, map layout structure, analyze component hierarchies, visualize frontend architecture, or create docs for AI understanding. Trigger on any request involving frontend structure, layout, or component organization documentation.
---

# Frontend Layout Docs Skill

A tool to help AI quickly understand and modify frontend code through layout documentation.

## Use Cases

- New projects needing layout documentation for AI understanding
- Existing projects needing supplementary layout explanations
- Team collaboration requiring unified frontend structure documentation
- AI needing to quickly locate components and modify code

## Document Structure

Generated layout docs are stored in `docs/layout/` directory:

```
docs/
├── layout/
│   ├── CLAUDE.md              # Index file
│   ├── Normal-layout.md       # Layout component
│   ├── Page1-layout.md        # Page 1
│   └── ...
└── screenshots/               # Optional: screenshots and annotations
    ├── CLAUDE.md
    └── Page1/
        ├── overview.png
        └── annotations.md
```

## Document Template

### Single Page Layout Template

```markdown
# [Page Name] Layout

> File path: `frontend/src/pages/[FileName].vue`
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

## Layout Dimensions

| Area | Size |
|------|------|
| Header | Height XXpx |
| Footer | Height XXpx |
| Left Sider | Width XXpx |
| Content | Adaptive |

## Component Mapping

### Main Structure

| Layout Area | Component/Element | File Location |
|-------------|-------------------|---------------|
| Header | n-layout-header | Page.vue:line |
| Left Sidebar | n-layout-sider | Page.vue:line |
| Content | n-tabs | Page.vue:line |
| Footer | n-layout-footer | Page.vue:line |

### Sub-components

| Component | File Location | Function |
|-----------|---------------|----------|
| ComponentA | components/ComponentA.vue | Description |

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

## Interactions

| Action | Trigger | Description |
|--------|---------|-------------|
| Click button | Event handler | Description |

## Related Files

### Script Files
- `scripts/Xxx.ts` - Description

### Component Files
- `components/Xxx.vue` - Description
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

### 1. Analyze Project Structure

First understand the project's tech stack and directory structure:

```bash
# View frontend directory structure
ls frontend/src/

# View page files
ls frontend/src/pages/

# View layout components
ls frontend/src/layout/

# View router config
cat frontend/src/router/index.ts
```

### 2. Read Key Files

For each page, read:
- Page component file (`.vue` / `.tsx`)
- Related script files (`scripts/`, `stores/`, `hooks/`)
- Sub-component files (`components/`)

### 3. Generate Layout Docs

Create documents in this order:
1. **Layout Component** - If there's a unified layout component (e.g., Normal.vue, Layout.vue)
2. **Main Pages** - Sorted by importance
3. **Index File** - Create CLAUDE.md last

### 4. Optional: Screenshots and Annotations

If screenshots are needed:
1. Start development server
2. Use Playwright to capture screenshots
3. Create annotation documents

### 5. Update CLAUDE.md

Add layout documentation reference in project root CLAUDE.md:

```markdown
## Frontend Layout Documentation

Layout visualization docs for understanding page structure:

| Page | Document | Description |
|------|----------|-------------|
| Outer Layout | [Normal-layout.md](docs/layout/Normal-layout.md) | Top navigation component |
| Page 1 | [Page1-layout.md](docs/layout/Page1-layout.md) | Description |
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
