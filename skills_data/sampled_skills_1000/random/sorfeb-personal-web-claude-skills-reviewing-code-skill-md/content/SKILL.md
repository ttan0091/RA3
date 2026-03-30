---
name: reviewing-code
description: |
  Code review with project-specific conventions for Xbox 360 portfolio site.
  Use when reviewing code, checking PRs, auditing files, or when user mentions
  "review", "check code", "audit", "PR review", "code quality", or "best practices".
---

# Code Review

Review code against project conventions and best practices.

## Review Workflow

```
- [ ] Step 1: Check critical rules (dev server, deps, console.log)
- [ ] Step 2: Verify TypeScript compilation
- [ ] Step 3: Frontend checks (if applicable)
- [ ] Step 4: Backend checks (if applicable)
- [ ] Step 5: Security review
- [ ] Step 6: Performance review
- [ ] Step 7: Generate findings report
```

## Critical Rule Violations (BLOCKERS)

These MUST be fixed before approval:

| Violation | Detection | Fix |
|-----------|-----------|-----|
| Dev server started | `npm run dev` in code | Remove, never auto-start |
| Unauthorized deps | New package.json entries | Remove or get approval |
| Console.log abuse | `console.log()` calls | Remove or use TRPCError |
| Missing Zod validation | tRPC input without `.input()` | Add Zod schema |
| Raw DB errors exposed | Prisma errors to client | Wrap with TRPCError |

## Frontend Review Checklist

```
Audio Integration:
- [ ] Every button/clickable has playSound()
- [ ] Hover states trigger hover sound
- [ ] Navigation uses navigateWithSound()

Styling:
- [ ] Uses CSS Modules (not inline styles)
- [ ] Responsive at 768px breakpoint
- [ ] Transitions: 0.3s hover, 0.5s major

Component Quality:
- [ ] 'use client' for interactive components
- [ ] React.memo for performance-critical
- [ ] TypeScript interfaces with JSDoc
- [ ] No any types
```

## Backend Review Checklist

```
API Security:
- [ ] All inputs validated with Zod
- [ ] protectedProcedure for auth-required
- [ ] Resource ownership checks
- [ ] Proper TRPCError codes

Query Optimization:
- [ ] select() used (not fetching all fields)
- [ ] Pagination for lists
- [ ] Indexes defined for queries

Error Handling:
- [ ] TRPCError with meaningful messages
- [ ] No raw errors exposed to client
- [ ] console.error only for critical issues
```

## Security Review

See [SECURITY.md](SECURITY.md) for detailed security checklist.

## Report Format

```markdown
## Code Review: [file/feature name]

### Critical Issues (Blockers)
- Issue 1: [description] - Line X
- Issue 2: [description] - Line Y

### Warnings
- Warning 1: [description]

### Suggestions
- Suggestion 1: [description]

### Passed Checks
- [x] TypeScript compiles
- [x] No console.log statements
- [x] Audio integration present
```
