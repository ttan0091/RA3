# Self-Directed Debugging: Example Workflows

## Example 1: Adding a New Feature (Frontend)

### User Request
"Add a user profile page with avatar upload"

### Skill-Guided Workflow

#### 1. Ask Clarifying Questions
```markdown
Claude uses AskUserQuestion:

❓ Before implementing, I have a few questions:

1. Avatar storage: Should I use a cloud service (S3, Cloudinary)
   or store locally? What's your preference?

2. File size limits: What's the maximum file size for avatars?
   (Recommended: 2-5MB)

3. Image formats: Should I support JPG, PNG, WebP? Any restrictions?

4. Validation: Client-side only, or server-side too?

5. Default avatar: Should users without avatars see a placeholder
   or initials-based avatar?
```

#### 2. Implement Based on Answers
```typescript
// After user responds: "Use Cloudinary, 5MB limit, JPG/PNG only,
// both client and server validation, initials-based placeholder"

// Implement ProfilePage.tsx, AvatarUpload.tsx, etc.
```

#### 3. Verify Implementation
```bash
# Step 1: Linter
$ npm run lint
Found 4 issues:
- Unused import 'useState' in ProfilePage.tsx
- Missing dependency 'userId' in useEffect

$ npm run lint:fix
✅ Auto-fixed 2 formatting issues
❌ 2 issues need manual fix

# Fix manually, then re-run
$ npm run lint
✅ All checks passed
```

```bash
# Step 2: Type Check
$ tsc --noEmit
✅ No type errors
```

```bash
# Step 3: Tests
$ npm test -- ProfilePage.spec.tsx --run
✅ 8/8 tests passed
```

```bash
# Step 4: Build
$ npm run build
✅ Build successful
```

#### 4. Browser Verification
```bash
$ npm run dev
Server running on http://localhost:3000
```

**Manual checks:**
- ✅ Navigate to /profile
- ✅ Click avatar upload button
- ✅ Select 8MB file → See error "File too large"
- ✅ Select valid 2MB JPG → Upload succeeds
- ✅ Check DevTools console → No errors
- ✅ Check Network tab → Cloudinary upload returns 200
- ✅ Refresh page → Avatar persists

#### 5. Report to User
```markdown
✅ Profile page with avatar upload completed and verified:

**Implementation:**
- Created ProfilePage.tsx with form layout
- AvatarUpload component with drag-and-drop
- Cloudinary integration with signed uploads
- Client + server validation (max 5MB, JPG/PNG only)
- Initials-based placeholder for users without avatars

**Verification Results:**
- Linter: ✅ Passed (auto-fixed 2 issues, manually fixed 2)
- Type Check: ✅ Passed
- Unit Tests: ✅ 8/8 passed
- Build: ✅ Success
- Browser Testing:
  - ✅ File size validation works (rejected 8MB file)
  - ✅ Upload succeeds with valid file
  - ✅ No console errors
  - ✅ Avatar persists after refresh

Ready to commit!
```

---

## Example 2: Debugging a Bug

### User Request
"The checkout button doesn't work in production but works locally"

### Skill-Guided Workflow

#### 1. Ask for Context
```markdown
❓ To debug effectively, I need some information:

1. What exactly happens when users click the button?
   - Nothing happens?
   - Error message?
   - Page redirects incorrectly?

2. Do you see errors in browser console in production?
   (Can you share screenshot or error text?)

3. Is this affecting all users or specific browsers?

4. When did this start? After a recent deployment?

5. Are there differences between local and production env vars?
```

#### 2. Reproduce Locally
```bash
# Try to reproduce with production-like conditions
$ NODE_ENV=production npm run build
$ npm run preview  # Serve production build locally
```

Check DevTools:
```
Console shows:
❌ Uncaught ReferenceError: process is not defined
   at CheckoutButton.tsx:42
```

#### 3. Identify Root Cause
```typescript
// Line 42 in CheckoutButton.tsx
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'
```

**Problem:** Accessing `process.env` in client-side code, which only works in dev mode due to webpack.DefinePlugin behavior.

#### 4. Fix the Issue
```typescript
// Fixed version - use runtime config instead
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000'
```

#### 5. Verify Fix
```bash
# Linter
$ npm run lint
✅ Passed

# Build (crucial for this bug)
$ npm run build
✅ Build successful

# Preview production build
$ npm run preview
```

Browser check:
- ✅ Click checkout button → Works correctly
- ✅ Console → No errors
- ✅ Network tab → API call succeeds

#### 6. Report Fix
```markdown
✅ Bug fixed and verified:

**Root Cause:**
CheckoutButton.tsx:42 was using `process.env.NEXT_PUBLIC_API_URL` which
doesn't exist in production builds (only in dev mode).

**Fix:**
Changed to `import.meta.env.VITE_API_URL` which works in both dev and prod.

**Verification:**
- Linter: ✅ Passed
- Production build: ✅ Success
- Preview mode: ✅ Checkout button works
- Console: ✅ No errors
- Network: ✅ API call succeeds

Safe to deploy!
```

---

## Example 3: Refactoring with Quality Checks

### User Request
"Refactor the authentication code to use React Context instead of prop drilling"

### Skill-Guided Workflow

#### 1. Ask About Scope
```markdown
❓ Before refactoring, let me clarify:

1. Should I also migrate the theme context to the same pattern?
   (I see it's also using prop drilling)

2. Do you want to keep the existing API structure, or can I
   improve the naming/organization?

3. Should auth state persist in localStorage/sessionStorage?

4. Are there any components that should NOT have access to auth?
   (Some teams restrict certain components for security)
```

#### 2. Implement Refactor
```typescript
// Create AuthContext.tsx
// Refactor 15 components to use useAuth() hook
// Remove props from component signatures
```

#### 3. Progressive Verification

**After creating AuthContext:**
```bash
$ npm run lint
❌ 3 unused imports in old files

$ npm run lint:fix
✅ Auto-fixed

$ tsc --noEmit
✅ No type errors
```

**After refactoring first 5 components:**
```bash
$ npm test -- --run Auth
✅ 24/24 tests pass

$ npm run dev
```
Check browser:
- ✅ Login still works
- ✅ Protected routes still work

**After all components refactored:**
```bash
$ npm run lint
✅ Passed

$ tsc --noEmit
✅ Passed

$ npm test -- --run
✅ 147/147 tests pass

$ npm run build
✅ Build successful
```

#### 4. Comprehensive Browser Check
- ✅ Login flow works
- ✅ Logout works
- ✅ Protected route redirect works
- ✅ Auth state persists on refresh
- ✅ No console errors
- ✅ No memory leaks (check DevTools Memory tab)

#### 5. Report Changes
```markdown
✅ Authentication refactor completed:

**Changes:**
- Created AuthContext with useAuth() hook
- Refactored 15 components to remove prop drilling
- Removed 47 prop declarations
- Code is now ~200 lines shorter

**Verification:**
- Linter: ✅ Passed (auto-fixed 3 unused imports)
- Type Check: ✅ Passed
- Tests: ✅ 147/147 passing (no regressions)
- Build: ✅ Success
- Browser:
  - ✅ Login/logout working
  - ✅ Protected routes working
  - ✅ State persistence working
  - ✅ No console errors
  - ✅ No memory leaks

Safe to merge!
```

---

## Common Questions to Ask

### Architecture Decisions
- "Should I use a library (X) or implement custom solution?"
- "Where should this validation live - client, server, or both?"
- "Should this be a hook, component, or utility function?"

### Error Handling
- "What should happen when the API fails?"
- "Should I show a toast notification or inline error?"
- "Do you want error retry logic? How many retries?"

### Performance
- "Should I implement pagination or infinite scroll?"
- "Do you want debouncing/throttling on this input?"
- "Should this data be cached? For how long?"

### UX Details
- "What should the loading state look like?"
- "Should this be a modal or a new page?"
- "Do you want keyboard shortcuts for this action?"

### Data & State
- "Where should this state live - local, context, or global store?"
- "Should this data persist across page refreshes?"
- "Do you want optimistic updates or wait for server confirmation?"

---

## Verification Checklist

Use this checklist for every change:

### Automated Checks
- [ ] `npm run lint` passes (or auto-fixed)
- [ ] `tsc --noEmit` passes
- [ ] `npm test -- --run` passes
- [ ] `npm run build` succeeds

### Browser Checks (Frontend)
- [ ] Start dev server
- [ ] Open DevTools (F12)
- [ ] Test the actual functionality
- [ ] Check Console tab for errors
- [ ] Check Network tab for failed requests
- [ ] Test on mobile viewport
- [ ] No hydration errors

### Code Quality
- [ ] No debug code left (console.log, debugger)
- [ ] No commented code blocks
- [ ] Imports are organized
- [ ] Error handling is present
- [ ] Edge cases are handled

### Report Format
```markdown
✅ [Feature Name] completed and verified:

**Implementation:**
- [What was built]

**Verification:**
- Linter: ✅/❌
- Type Check: ✅/❌
- Tests: ✅/❌ [X/Y passed]
- Build: ✅/❌
- Browser: ✅/❌ [specific checks]

[Any issues or notes]
```
