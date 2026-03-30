---
name: feature
description: Spec-driven feature development workflow with documentation consultation
disable-model-invocation: true
argument-hint: '"description" | --continue | --verify'
---

# Feature Development Workflow

Structured 7-phase workflow for implementing features with Astro best practices.

## Prerequisites

- **astro-docs** MCP - For documentation lookup
- **astro** MCP (optional) - For project state

## Usage

```
/feature "Add dark mode toggle"     # Start new feature
/feature --continue                  # Resume in-progress feature
/feature --verify                    # Run verification only
```

## The 7 Phases

### Phase 1: CLARIFY
Understand requirements fully before coding.

**Actions:**
- Parse the feature description
- Identify ambiguities
- Ask clarifying questions
- Confirm requirements with user

**Output:**
```
FEATURE: "Add dark mode toggle"

Questions:
1. Should dark mode persist across sessions?
2. Should it respect system preference initially?
3. Where should the toggle be placed?
```

### Phase 2: CONSULT
Query astro-docs for current best practices.

**Actions:**
- Search documentation for relevant patterns
- Check for Astro-specific approaches
- Identify recommended integrations
- Note any gotchas or common mistakes

**Output:**
```
Documentation found:
- CSS Variables for Theming (recommended approach)
- View Transitions API for smooth theme switch
- client:load for immediate interaction
```

### Phase 3: ANALYZE
Understand existing code and patterns.

**Actions:**
- Query astro MCP for project structure (if available)
- Read relevant existing files
- Identify files to modify
- Check for conflicts

**Output:**
```
Existing patterns:
- Layout: src/layouts/Base.astro
- Header: src/components/Header.astro
- Styles: src/styles/global.css

Files to modify: 3
New files to create: 2
```

### Phase 4: PLAN
Design the implementation approach.

**Actions:**
- Create step-by-step implementation plan
- List files to create/modify
- Estimate scope of changes
- Present to user for approval

**Output:**
```
Implementation Plan:
1. Create CSS variables in theme.css
2. Create ThemeToggle.astro component
3. Update Base.astro with theme script
4. Add toggle to Header.astro

Proceed? (yes/modify/cancel)
```

### Phase 5: EXECUTE
Build the feature following the plan.

**Actions:**
- Create new files
- Modify existing files
- Follow Astro best practices
- Use proper TypeScript types

**Output:**
```
[1/4] Creating src/styles/theme.css ✓
[2/4] Creating src/components/ThemeToggle.astro ✓
[3/4] Updating src/layouts/Base.astro ✓
[4/4] Updating src/components/Header.astro ✓
```

### Phase 6: VERIFY
Ensure the feature works correctly.

**Actions:**
- Run /astro-check if available
- Verify no TypeScript errors
- Check for build warnings
- Test feature functionality

**Output:**
```
Verification:
✓ TypeScript: No errors
✓ Build: Success
✓ Astro Check: Passed
✓ Feature: Working
```

### Phase 7: SHIP
Commit with a detailed message.

**Actions:**
- Stage changed files
- Generate descriptive commit message
- Include "Consulted: astro docs" reference
- Commit changes

**Output:**
```
Commit message:
feat: Add dark mode toggle with system preference support

- Add CSS custom properties for theming
- Create ThemeToggle component with icons
- Implement flash prevention script
- Persist preference in localStorage

Consulted: Astro docs on CSS Variables, View Transitions
```

## State Persistence

Feature progress is saved in `.cleo-web/feature-state.json`:
```json
{
  "currentFeature": {
    "description": "Add dark mode toggle",
    "phase": 5,
    "plan": [...],
    "filesCreated": [...],
    "filesModified": [...]
  }
}
```

Use `/feature --continue` to resume.

## Integration

- **With /astro-check**: Runs during VERIFY phase
- **With /task**: Creates follow-up tasks if needed
- **With /session**: Feature progress tracked in session

## Arguments
$ARGUMENTS
