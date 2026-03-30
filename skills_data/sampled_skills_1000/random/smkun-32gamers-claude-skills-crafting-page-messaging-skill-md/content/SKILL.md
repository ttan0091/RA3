---
name: crafting-page-messaging
description: |
  Writes conversion-focused messaging for pages and key CTAs in the 32Gamers portal.
  Use when: writing headlines, CTAs, loading states, error messages, empty states, form labels, page titles, or any user-facing copy.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, mcp__serena__find_file, mcp__serena__search_for_pattern, mcp__serena__get_symbols_overview, mcp__serena__find_symbol, mcp__serena__replace_symbol_body, mcp__tavily__tavily_search
---

# Crafting Page Messaging

Writes conversion-focused copy for the 32Gamers cyberpunk portal. All messaging follows the retro-futuristic gaming theme with command-line aesthetics.

## Quick Start

### Headlines Use Command Syntax

```html
<!-- GOOD - Cyberpunk command aesthetic -->
<h1 class="cyber-title">MISSION CONTROL</h1>
<div class="subtitle">// SELECT YOUR MISSION</div>

<!-- BAD - Generic web copy -->
<h1>Welcome to Our Portal</h1>
<p>Choose a game to play</p>
```

### Loading States Signal Progress

```html
<!-- GOOD - Themed, specific -->
<p class="loading-text">
    <span class="loading-bracket">[</span>
    INITIALIZING NEURAL LINK
    <span class="loading-bracket">]</span>
</p>

<!-- BAD - Generic -->
<p>Loading...</p>
```

## Key Concepts

| Element | Pattern | Example |
|---------|---------|---------|
| Headlines | ALL CAPS + command syntax | `MISSION CONTROL` |
| Subtitles | `//` comment prefix | `// SELECT YOUR MISSION` |
| Brackets | Wrap status text | `[ LOADING ]` |
| Actions | Imperative verbs | `Sign in`, `Add App`, `Retry` |
| Errors | Technical but clear | `NEURAL LINK FAILED` |

## Messaging Locations

| File | Elements |
|------|----------|
| `index.html:56-61` | Main headline, subtitle |
| `index.html:71-75` | Loading state copy |
| `firebase-admin.html:21-23` | Login section messaging |
| `firebase-admin.html:51-71` | Form labels, placeholders |
| `scripts/app.js:107-113` | Error message templates |
| `scripts/app.js:163-165` | Search placeholder |

## Common Patterns

### CTAs Follow Action Hierarchy

```html
<!-- Primary: Clear imperative -->
<button class="btn-primary">Add App</button>
<button class="login-btn">Sign in with Google</button>

<!-- Secondary: Navigation context -->
<button class="btn-secondary">← Back to Portal</button>
<button class="btn-secondary">Cancel Edit</button>
```

### Error Messages Explain + Offer Action

```javascript
// GOOD - Problem + solution
this.showError('Unable to load apps. Please check your internet connection or contact the administrator.');

// BAD - Just the error
this.showError('Network error');
```

### Status Messages Match Severity

```javascript
showStatus('Apps loaded successfully!', 'success');
showStatus('Please fill in all fields', 'error');
showStatus('Opening sign-in popup...', 'info');
```

## Voice Guidelines

| DO | DON'T |
|----|-------|
| `MISSION CONTROL` | `Home Page` |
| `INITIALIZING NEURAL LINK` | `Loading apps...` |
| `Admin Access Required` | `Please log in` |
| `Sign in with Google` | `Login` |
| `← Back to Portal` | `Go Back` |

## See Also

- [conversion-optimization](references/conversion-optimization.md)
- [content-copy](references/content-copy.md)
- [distribution](references/distribution.md)
- [measurement-testing](references/measurement-testing.md)
- [growth-engineering](references/growth-engineering.md)
- [strategy-monetization](references/strategy-monetization.md)

## Related Skills

For implementing copy in code, see the **vanilla-javascript** skill.
For styling message elements, see the **css** skill.
For form interactions and auth flows, see the **google-oauth** skill.
For empty states and first-run experiences, see the **designing-onboarding-paths** skill.
For tracking message effectiveness, see the **instrumenting-product-metrics** skill.