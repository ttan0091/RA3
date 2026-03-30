---
name: git-commit
description: Create atomic, conventional git commits following the .gitmessage template. Enforces type checking and linting before commit.
trigger: /commit
---

# Git Commit

Create proper atomic commits with conventional message format for Health Tracker 9000.

## Environment Notes

- **OS**: Windows
- **Node Packages**: Managed via `npm` (not venv)
- **Pre-commit Hooks**: Husky + lint-staged (auto-runs on `git commit`)

## Conventional Commit Format

Follow `.gitmessage` template structure:

```
<type>(<scope>): <subject>

<body>

<references>
```

### Commit Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Formatting/style changes (not code changes)
- `refactor:` Code restructuring without new features
- `perf:` Performance improvements
- `test:` Test additions/updates
- `chore:` Build/tooling/dependency changes
- `ci:` CI/CD configuration changes

### Scope Examples

Use project-specific scopes:

- `api:` API routes and endpoints
- `repo:` Repository/database layer
- `db:` Database schema or migrations
- `store:` Zustand state management
- `meal:` Meal logging feature
- `supplement:` Supplement tracking feature
- `profile:` User profile feature
- `analytics:` Analytics and reporting
- `ui:` UI components and styling
- `form:` Form components
- `hook:` Custom React hooks
- `types:` TypeScript types
- `util:` Utility functions

## Atomic Commit Checklist

Ensure BEFORE committing:

- ✓ One logical change per commit
- ✓ Each commit independently testable
- ✓ No mixed concerns (e.g., feat + refactor in same commit)
- ✓ All tests pass locally (`npm test`)
- ✓ Linting passes (`npm run lint`)
- ✓ TypeScript passes (`npx tsc --noEmit`)
- ✓ Related files modified together
- ✓ Tests added/updated for code changes

## Pre-commit Automation

Your Husky hooks automatically run on `git commit`:

1. **ESLint + Prettier** - Formats and lints changed files via lint-staged
2. **TypeScript** - Full type checking via `npx tsc --noEmit`
3. **Validation** - Exits if any check fails (must fix and try again)

**No manual linting needed** - hooks handle it automatically.

## Commit Examples

### Simple Feature

```
feat(meal): add allergen conflict detection
```

### Bug Fix

```
fix(form): prevent duplicate food entries
```

### With Body and References

```
feat(api): implement daily summary endpoint

Aggregates daily nutritional and supplement data,
returns health score and nutrient totals for dashboard.

Closes #123
```

### Database Change

```
chore(db): add indexes to meal_logs table
```

### Component Refactor

```
refactor(analytics): extract chart logic to hook
```

## How to Commit

1. Stage changes: `git add .`
2. Start commit: `git commit` (template auto-loads)
3. Edit message in editor (follow template)
4. Save and exit
5. Pre-commit hooks run automatically
6. If checks fail, fix issues and run `git commit` again

**Tips**:

- Keep subject line ≤ 50 characters
- Body lines ≤ 72 characters
- Describe _why_, not _what_ (code shows the what)
- One logical change per commit
- Always add tests for code changes

---

**Last Updated**: 2026-02-04
