---
name: Self-Directed Debugging
description: Autonomous development workflow that proactively asks questions, verifies implementation with tools, and auto-fixes linter errors. Use when implementing features to ensure quality through self-driven verification.
version: 0.1.0
---

# Self-Directed Debugging Skill

## Overview

This skill enables Claude Code to work autonomously with proactive quality assurance. It emphasizes asking clarifying questions, verifying implementations, and automatically fixing issues.

## Core Principles

### 1. Ask First, Code Later

**ALWAYS ask clarifying questions when:**
- Requirements are ambiguous or underspecified
- Multiple implementation approaches exist
- Design decisions impact architecture
- Edge cases are unclear
- Dependencies or tools are unfamiliar

**Use AskUserQuestion tool proactively:**
```markdown
Examples:
- "Should I use Redux or Context API for state management?"
- "Do you want error boundaries at the page or component level?"
- "Should validation happen on the client, server, or both?"
- "What should happen if the API times out?"
```

**DON'T:**
- Make assumptions without asking
- Implement the first solution that comes to mind
- Skip questions to "save time"
- Guess at business logic requirements

### 2. Verify Everything

After implementing any feature, **ALWAYS perform these verification steps:**

#### A. Linter Check
```bash
# Run linter immediately after changes
npm run lint
# or
pnpm lint
# or
eslint src/

# If errors found, fix them automatically
npm run lint:fix
```

#### B. Type Check
```bash
# Verify TypeScript types
tsc --noEmit
# or
npm run typecheck
```

#### C. Unit Tests
```bash
# Run relevant tests
npm test -- --run
# or specific test file
npm test -- path/to/test.spec.ts
```

#### D. Build Check
```bash
# Ensure build succeeds
npm run build
```

#### E. Browser Verification (Frontend)

**For web applications, ALWAYS:**

1. **Start dev server and verify in browser**
```bash
npm run dev
```

2. **Check browser console for errors**
   - Open DevTools (F12)
   - Look for console errors (red messages)
   - Check network tab for failed requests
   - Verify no warnings

3. **Test actual functionality**
   - Click buttons and links
   - Fill out forms
   - Verify API calls work
   - Check responsive design

4. **Common checks:**
   - No hydration errors
   - No 404s in network tab
   - Images load correctly
   - CSS applies as expected

#### F. Report Findings

**ALWAYS report verification results to user:**
```markdown
✅ Verification Results:
- Linter: Passed (auto-fixed 3 formatting issues)
- Type Check: Passed
- Tests: 12/12 passed
- Build: Success
- Browser: ✅ No console errors, functionality works as expected
```

### 3. Auto-Fix Linter Errors

**When linter errors are found:**

1. **Attempt automatic fix first:**
```bash
npm run lint:fix
# or
eslint --fix src/
```

2. **If auto-fix doesn't work, manually fix:**
   - Read error messages carefully
   - Fix common issues:
     - Unused imports → Remove them
     - Missing dependencies → Add to useEffect deps
     - Formatting → Run prettier
     - Naming conventions → Follow project style

3. **Report what was fixed:**
```markdown
Fixed linter errors:
- Removed 5 unused imports
- Added missing React dependencies to useEffect
- Fixed 12 indentation issues
```

### 4. Debugging Workflow

**When encountering issues:**

#### Step 1: Reproduce
- Clearly identify the problem
- Note exact error messages
- Identify which file/function fails

#### Step 2: Investigate
```bash
# Check logs
npm run dev  # Watch console output

# Run specific tests
npm test -- --run ComponentName

# Check type errors
tsc --noEmit
```

#### Step 3: Ask if Unclear
Use AskUserQuestion if:
- Error message is cryptic
- Root cause is unclear
- Multiple solutions exist
- Need user preference on fix approach

#### Step 4: Fix & Verify
- Implement fix
- Run full verification workflow (linter, tests, build)
- Verify in browser if frontend
- Report results to user

### 5. Proactive Issue Detection

**BEFORE committing code, check:**

- [ ] No console.log() statements left behind
- [ ] No commented-out code blocks
- [ ] No TODO comments without context
- [ ] All imports are used
- [ ] No hardcoded values that should be config
- [ ] Error handling is present
- [ ] Loading states are handled
- [ ] Edge cases are covered

## Quick Reference Commands

### Verification Commands
```bash
# All-in-one verification
npm run lint && npm run typecheck && npm test -- --run && npm run build

# Frontend verification
npm run dev  # Then manually check browser DevTools
```

### Common Linter Fixes
```bash
# ESLint
eslint --fix src/

# Prettier
prettier --write src/

# Both
npm run format  # if configured
```

### Browser DevTools Shortcuts
- `F12` or `Cmd+Option+I` - Open DevTools
- `Cmd+Shift+C` - Inspect element
- `Cmd+K` - Clear console
- `Cmd+R` - Hard reload
- `Cmd+Shift+R` - Hard reload (clear cache)

## Integration with Development

### When to Use This Skill

**Always active for:**
- Feature implementation
- Bug fixes
- Refactoring
- Code reviews

**Especially critical for:**
- Frontend development (requires browser verification)
- API changes (requires testing)
- Type changes (requires typecheck)
- New dependencies (requires build check)

### Workflow Example

```markdown
User: "Add a dark mode toggle to the settings page"

Claude:
1. ❓ ASK: "Should dark mode preference persist across sessions?
   Should it respect system preferences?"

2. 💻 IMPLEMENT: Create toggle component and theme context

3. ✅ VERIFY:
   - Run: npm run lint:fix
   - Run: tsc --noEmit
   - Run: npm test -- --run
   - Run: npm run dev
   - Open browser DevTools
   - Toggle dark mode
   - Check for console errors
   - Verify localStorage persistence

4. 📊 REPORT:
   "✅ Dark mode toggle implemented and verified:
   - Linter: Passed (auto-fixed 2 issues)
   - Types: Passed
   - Tests: All passing
   - Browser: No console errors
   - Functionality: Toggle works, persists in localStorage,
     respects system preference on first load"
```

## Anti-Patterns to Avoid

❌ **Don't:**
- Skip verification steps to "go faster"
- Assume code works without testing
- Ignore linter warnings
- Commit without running build
- Forget to check browser console
- Make assumptions instead of asking

✅ **Do:**
- Ask questions proactively
- Run full verification suite
- Auto-fix linter errors immediately
- Test in actual browser
- Report verification results
- Fix issues before moving to next task

## Tool Usage

### Priority Order for Verification

1. **Linter** (fastest, catches style issues)
2. **Type Check** (fast, catches type errors)
3. **Unit Tests** (medium, catches logic errors)
4. **Build** (slower, catches integration issues)
5. **Browser** (slowest, catches runtime issues)

Run them in order - fix issues at each level before proceeding.

## Summary

This skill transforms Claude Code into a proactive, quality-focused developer that:
- **Asks** clarifying questions before coding
- **Verifies** all changes with automated tools
- **Tests** functionality in real environments
- **Fixes** issues automatically when possible
- **Reports** findings transparently

By following this workflow, you ensure high-quality, well-tested code with minimal back-and-forth.
