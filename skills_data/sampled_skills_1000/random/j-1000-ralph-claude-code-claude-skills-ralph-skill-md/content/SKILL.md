---
name: ralph
description: Convert markdown PRDs to prd.json format for autonomous Ralph loop execution. Use after creating a PRD with the prd skill.
---

# Ralph Skill

Convert markdown PRDs into structured JSON for autonomous Ralph loop execution.

## Purpose

Transform a markdown PRD into `prd.json` with properly structured user stories that Ralph can execute autonomously.

## Input

A markdown PRD file (typically from `tasks/prd-[feature-name].md`)

## Output

A `prd.json` file in the project root with this structure:

```json
{
  "project": "ProjectName",
  "branchName": "ralph/feature-name",
  "description": "Brief feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Short descriptive title",
      "description": "As a [user], I want [action] so that [benefit]",
      "acceptanceCriteria": [
        "Specific, testable criterion 1",
        "Specific, testable criterion 2",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Story Sizing Rules

Each story must be completable in ONE context window. Split large stories:

### Too Big (Split These)
- "Build the entire dashboard"
- "Add authentication"
- "Refactor the API"
- "Create the settings page"

### Right-Sized Stories
- "Add status column to tasks table with migration"
- "Create StatusBadge component"
- "Add status dropdown to task row"
- "Connect status dropdown to server action"
- "Add status filter to task list"

## Acceptance Criteria Guidelines

Every story MUST include:
- At least one functional criterion
- `"Typecheck passes"` (for TypeScript projects)
- `"Verify in browser using dev-browser skill"` (for UI stories)

Good criteria are:
- Specific and testable
- Observable (can be verified)
- Independent (don't depend on other stories)

### Examples

**Good:**
```json
"acceptanceCriteria": [
  "Status column added with type: 'pending' | 'in_progress' | 'done'",
  "Default value is 'pending'",
  "Migration runs without errors",
  "Typecheck passes"
]
```

**Bad:**
```json
"acceptanceCriteria": [
  "Status works",
  "Looks good",
  "No bugs"
]
```

## Priority Assignment

- **Priority 1**: Database/schema changes (must come first)
- **Priority 2**: Core backend logic/server actions
- **Priority 3**: Basic UI components
- **Priority 4**: UI interactions and state
- **Priority 5**: Polish, filters, edge cases

## Workflow

1. Read the markdown PRD
2. Extract user stories from requirements
3. Break large stories into smaller ones
4. Add proper acceptance criteria to each
5. Assign priorities (dependencies first)
6. Generate `prd.json`
7. Save to project root

## Example Conversion

**Input PRD excerpt:**
```markdown
## Functional Requirements
1. Users can see task status on each card
2. Users can change status from a dropdown
3. Users can filter by status
```

**Output prd.json:**
```json
{
  "project": "TaskApp",
  "branchName": "ralph/task-status",
  "description": "Add task status tracking with visual indicators",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add status field to tasks table",
      "description": "As a developer, I need to store task status in the database",
      "acceptanceCriteria": [
        "Add status column: 'pending' | 'in_progress' | 'done'",
        "Default value is 'pending'",
        "Migration runs successfully",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Display status badge on task cards",
      "description": "As a user, I want to see task status at a glance",
      "acceptanceCriteria": [
        "Each task card shows colored status badge",
        "Colors: gray=pending, blue=in_progress, green=done",
        "Typecheck passes",
        "Verify in browser using dev-browser skill"
      ],
      "priority": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "title": "Add status dropdown to task rows",
      "description": "As a user, I want to change status from the task list",
      "acceptanceCriteria": [
        "Each row has status dropdown",
        "Selecting new status saves immediately",
        "UI updates without page refresh",
        "Typecheck passes",
        "Verify in browser using dev-browser skill"
      ],
      "priority": 3,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-004",
      "title": "Filter tasks by status",
      "description": "As a user, I want to see only tasks with a specific status",
      "acceptanceCriteria": [
        "Filter dropdown with: All, Pending, In Progress, Done",
        "Selecting filter updates task list",
        "Filter persists in URL params",
        "Typecheck passes",
        "Verify in browser using dev-browser skill"
      ],
      "priority": 4,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## After Conversion

Tell the user:
1. Review `prd.json` to ensure stories are right-sized
2. Run Ralph with: `./scripts/ralph/ralph.sh 25`
3. Monitor progress in `progress.txt`
