# Content Copy Reference

## Contents
- Voice and Tone Guidelines
- Headline Writing Patterns
- Microcopy Standards
- Form Label Best Practices
- Status Message Templates

## Voice and Tone Guidelines

The 32Gamers portal uses cyberpunk gaming vernacular mixed with command-line aesthetics.

### Brand Voice Elements

| Element | Pattern | Example |
|---------|---------|---------|
| Headlines | Military/gaming command | `MISSION CONTROL` |
| Comments | Code syntax | `// SELECT YOUR MISSION` |
| Status | Bracketed tech speak | `[ INITIALIZING ]` |
| Actions | Clear imperatives | `Sign in`, `Add App` |
| Errors | Technical but helpful | `Neural link failed - retry connection` |

### DO: Match the Cyberpunk Aesthetic

```html
<!-- Themed copy that fits -->
<title>32GAMERS // MISSION CONTROL</title>
<h1 class="cyber-title">MISSION CONTROL</h1>
<div class="subtitle">// SELECT YOUR MISSION</div>
```

### DON'T: Generic Web Copy

```html
<!-- Breaks immersion -->
<title>32Gamers - Home</title>
<h1>Welcome to 32Gamers</h1>
<p>Choose a game below</p>
```

## Headline Writing Patterns

### Primary Headlines: ALL CAPS Command Style

```html
<!-- index.html:56-58 -->
<h1 class="cyber-title">
    <span class="glitch" data-text="MISSION CONTROL">MISSION CONTROL</span>
</h1>
```

**Why glitch text needs data-text:** The CSS glitch effect duplicates text via pseudo-elements. Keep `data-text` and content identical.

### Secondary Headlines: Standard Case

```html
<!-- firebase-admin.html - Admin sections -->
<h3>Admin Access Required</h3>
<h3>Add New App</h3>
<h3>Current Apps</h3>
```

**Rule:** Only the main portal title uses ALL CAPS + glitch. Admin panel uses standard capitalization for scannability.

## Microcopy Standards

### Loading States

```html
<!-- GOOD - Themed status -->
<p class="loading-text">
    <span class="loading-bracket">[</span>
    INITIALIZING NEURAL LINK
    <span class="loading-bracket">]</span>
</p>

<!-- BAD - Plain status -->
<p>Loading apps...</p>
```

### Empty States

```html
<!-- firebase-admin.html:268-269 -->
<p style="text-align: center; opacity: 0.7;">
    No apps found. Add your first app above!
</p>
```

**Pattern:** Empty states should guide next action, not just state the problem.

### Tooltips and Titles

```html
<!-- index.html:46 - Power-user hint -->
<div class="admin-icon" title="Admin Access [CTRL+ALT+A]">

<!-- scripts/app.js:79 - Accessibility context -->
button.setAttribute('title', app.description);
```

## Form Label Best Practices

### Labels Should Be Scannable

```html
<!-- firebase-admin.html:52-71 -->
<label for="appId">App ID:</label>
<label for="appName">App Name:</label>
<label for="appUrl">App URL:</label>
<label for="appImage">Image Filename:</label>
<label for="appDescription">Description:</label>
```

### Placeholders Show Format Examples

```html
<input type="text" id="appId" placeholder="my-new-app">
<input type="text" id="appUrl" placeholder="MyNewApp/index.html">
<input type="text" id="appImage" placeholder="my-app-icon.png">
<textarea id="appDescription" placeholder="Brief description"></textarea>
```

**Rule:** Placeholders demonstrate expected format, not duplicate the label.

## Status Message Templates

### Success Messages

```javascript
showStatus('Apps loaded successfully!', 'success');
showStatus('App added successfully!', 'success');
showStatus('App updated successfully!', 'success');
showStatus('App removed successfully!', 'success');
showStatus('Sign-in successful!', 'success');
```

**Pattern:** Past tense + exclamation for completed actions.

### Error Messages

```javascript
showStatus('Please fill in all fields', 'error');
showStatus('App ID already exists', 'error');
showStatus('Please login first', 'error');
showStatus(`Login failed: ${error.message}`, 'error');
```

**Pattern:** Clear problem statement. Include error details when available.

### Info Messages

```javascript
showStatus('Loading apps...', 'info');
showStatus('Opening sign-in popup...', 'info');
showStatus('Sign-in cancelled.', 'info');
```

**Pattern:** Present progressive for ongoing actions, past for completed.