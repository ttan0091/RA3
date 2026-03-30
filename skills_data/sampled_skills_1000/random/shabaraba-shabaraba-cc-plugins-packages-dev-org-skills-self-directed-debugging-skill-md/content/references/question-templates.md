# Question Templates for Proactive Clarification

## When to Ask Questions

**ALWAYS ask when:**
- Multiple valid approaches exist
- Requirements are ambiguous
- Edge cases aren't specified
- Design impacts architecture
- User preference matters

**NEVER assume:**
- Business logic rules
- UX/UI preferences
- Error handling strategies
- Performance requirements

---

## Question Templates by Category

### 1. Architecture & Design

#### State Management
```markdown
❓ State Management Approach:

I can implement this using:
1. Local component state (simplest)
2. React Context (medium complexity)
3. Redux/Zustand (most powerful)

Which approach do you prefer? Consider:
- How many components need this data?
- Does it need to persist?
- Will it grow complex over time?
```

#### Component Structure
```markdown
❓ Component Organization:

Should I:
1. Create a single component with multiple sub-components
2. Separate into multiple standalone components
3. Use composition with slots/children

What's your preference for maintainability?
```

#### API Integration
```markdown
❓ API Integration Strategy:

How should I handle data fetching?
1. Client-side fetch with useEffect
2. Server-side fetch (Next.js getServerSideProps)
3. Static generation with revalidation
4. React Query/SWR for caching

Also:
- Should I implement request deduplication?
- What's the cache TTL?
```

### 2. Error Handling

#### Error Display
```markdown
❓ Error Handling UX:

When errors occur, should I:
1. Show toast notification (non-blocking)
2. Inline error message (contextual)
3. Error boundary with fallback UI
4. Redirect to error page

Also:
- Should errors auto-dismiss or require user action?
- Do you want error reporting to a service (Sentry, etc.)?
```

#### Retry Logic
```markdown
❓ Retry Strategy:

For failed API requests:
1. No retry (fail immediately)
2. Auto-retry N times with exponential backoff
3. Show "Retry" button to user
4. Combination (auto-retry + manual option)

Your preference?
Also: Should retries be limited to specific error types (500s vs 400s)?
```

#### Validation Errors
```markdown
❓ Validation Strategy:

Should validation happen:
1. On blur (when user leaves field)
2. On submit (when form submitted)
3. Real-time (as user types)
4. Combination (real-time for some, on blur for others)

Also:
- Client-side only, or also server-side?
- Should we show all errors at once or one at a time?
```

### 3. Performance & Optimization

#### Data Loading
```markdown
❓ Loading Strategy:

For large datasets, should I implement:
1. Pagination (classic page-by-page)
2. Infinite scroll (load more on scroll)
3. Virtual scrolling (render only visible items)
4. Load all upfront with client-side filtering

Consider:
- Typical dataset size?
- User expectation (browsing vs searching)?
```

#### Caching
```markdown
❓ Caching Strategy:

Should I cache this data?
1. No caching (always fresh)
2. Short-term cache (1-5 minutes)
3. Long-term cache (hours/days)
4. Cache with manual invalidation

Also:
- Should cache persist across page refreshes (localStorage)?
- When should cache be invalidated (on mutation, time-based)?
```

#### Code Splitting
```markdown
❓ Bundle Optimization:

This feature is quite large. Should I:
1. Include in main bundle (faster for frequent users)
2. Code-split/lazy load (better initial load)
3. Preload (middle ground)

What's the expected usage frequency?
```

### 4. UX/UI Details

#### Loading States
```markdown
❓ Loading Experience:

While loading, should I show:
1. Spinner (simple)
2. Skeleton screen (content-aware)
3. Progress bar (if progress is measurable)
4. Optimistic UI (assume success, rollback if fails)

Your preference?
```

#### Confirmation Dialogs
```markdown
❓ Destructive Action Confirmation:

For [delete/archive/etc.], should I:
1. Show confirmation modal
2. Inline confirmation (expand with "Are you sure?")
3. Undo option (delete, then show undo toast)
4. No confirmation (trust user)

How cautious should we be?
```

#### Responsive Behavior
```markdown
❓ Mobile Layout:

On mobile screens, this component could:
1. Stack vertically
2. Horizontal scroll
3. Collapse with accordion
4. Show simplified version

What's best for your users?
```

#### Keyboard Navigation
```markdown
❓ Accessibility:

Should I implement keyboard shortcuts for this?
Examples:
- Enter to submit
- Escape to close
- Arrow keys to navigate
- Tab to focus next

Required level: Basic accessibility or power-user features?
```

### 5. Data & Business Logic

#### Data Persistence
```markdown
❓ Data Persistence:

Should this data:
1. Save automatically on change
2. Save on explicit "Save" button click
3. Persist locally (localStorage) only
4. Sync to server immediately

Also:
- What happens if save fails?
- Should we show "Unsaved changes" warning?
```

#### Filtering & Sorting
```markdown
❓ Data Filtering:

Should filtering/sorting happen:
1. Client-side (faster but limited to loaded data)
2. Server-side (slower but handles large datasets)
3. Hybrid (client-side with server fallback)

Typical dataset size?
Also: Should filters persist in URL for sharing?
```

#### Permissions
```markdown
❓ Access Control:

Who can perform this action?
1. All authenticated users
2. Users with specific role
3. Only resource owner
4. Admin only

Also:
- What should unauthorized users see (hide feature, show disabled, show error)?
```

### 6. Edge Cases

#### Empty States
```markdown
❓ Empty State Handling:

When there's no data, should I show:
1. Empty state message with CTA ("Add your first item")
2. Placeholder/skeleton
3. Tutorial/onboarding
4. Nothing (just empty space)

What guides the user best?
```

#### Concurrent Actions
```markdown
❓ Concurrent Editing:

If two users edit the same data simultaneously:
1. Last write wins (simple, possible data loss)
2. Optimistic locking (detect conflicts, ask user)
3. Real-time sync (operational transforms, CRDT)
4. Lock resource while editing

Expected concurrency level?
```

#### Network Offline
```markdown
❓ Offline Behavior:

When network is unavailable:
1. Show error immediately
2. Queue operations, sync when online
3. Fully offline-capable (service worker + indexedDB)
4. Prevent usage (disable features)

How critical is offline support?
```

### 7. Testing & Quality

#### Test Coverage
```markdown
❓ Testing Approach:

For this feature, should I write:
1. Unit tests only (fast, isolated)
2. Integration tests (component + hooks)
3. E2E tests (full user flow)
4. All of the above

Your testing standards?
```

#### Browser Support
```markdown
❓ Browser Compatibility:

Should I support:
1. Modern browsers only (Chrome, Firefox, Safari, Edge - last 2 versions)
2. Include IE11 (requires polyfills)
3. Mobile browsers (Safari iOS, Chrome Android)
4. Specific requirements?

This affects technology choices (e.g., can I use CSS Grid, async/await).
```

---

## Multi-Question Template

For complex features, combine questions:

```markdown
❓ Before implementing [Feature Name], I need to clarify:

**Architecture:**
1. Should I use [Option A] or [Option B] for state management?
2. Where should validation live - client, server, or both?

**UX:**
3. What should the loading state look like (spinner vs skeleton)?
4. How should errors be displayed (toast vs inline)?

**Data:**
5. Should changes save automatically or on button click?
6. What happens if the API call fails?

**Edge Cases:**
7. What should users see when there's no data?
8. Should this work offline (queue operations)?

Please let me know your preferences so I can implement this correctly!
```

---

## After Implementation - Verification Questions

```markdown
✅ [Feature] implemented. Before I mark this complete:

**Quick verification questions:**
1. Should I run the E2E tests as well, or are unit tests sufficient?
2. I see 2 lint warnings (non-critical). Fix now or create issue?
3. The bundle size increased by 50KB. Is that acceptable?
4. Should I update the documentation/README?

Let me know if you'd like me to address any of these!
```

---

## Don't Ask Obvious Questions

**BAD - Don't ask:**
```markdown
❌ Should I use TypeScript? (if project is already TypeScript)
❌ Should I follow the linter rules? (always yes)
❌ Should I write tests? (always yes)
❌ Should variable names be descriptive? (obviously yes)
```

**GOOD - Do ask:**
```markdown
✅ Should I use Zod or Yup for schema validation?
✅ Should this component be server or client component?
✅ Should I create a new API endpoint or extend existing?
✅ What's the priority: performance or feature richness?
```

---

## Template Usage

Copy these templates and customize with:
1. Specific context from the user's request
2. Relevant options based on project tech stack
3. Concrete examples from the codebase
4. Trade-offs specific to the decision

**Example customization:**
```markdown
# Generic template:
"Should I use [State Management A] or [State Management B]?"

# Customized for project:
"Should I use Zustand (already used in auth module) or
create new React Context (simpler, no dependencies)?"
```

This makes questions more actionable and shows you've analyzed the options.
