# Distribution Reference

## Contents
- SEO Metadata Patterns
- Social Sharing Optimization
- Open Graph Implementation
- Portal Discovery Flow

## SEO Metadata Patterns

The 32Gamers portal is a static site hosted on ifastnet Ultimate. Core SEO elements are in HTML.

### Current Title Implementation

```html
<!-- index.html:6 -->
<title>32GAMERS // MISSION CONTROL</title>

<!-- firebase-admin.html:5 -->
<title>32Gamers Firebase Admin</title>
```

**Title best practices:**
- Main portal: Brand + primary descriptor
- Admin: Brand + functional descriptor
- Keep under 60 characters

### WARNING: Missing Meta Descriptions

**Detected:** No `<meta name="description">` tags in HTML files.

**Impact:** Search engines will auto-generate descriptions from page content, which may not be optimal.

### Recommended Addition

```html
<!-- index.html - Add after title -->
<meta name="description" content="32Gamers gaming portal - your mission control for browser games and apps. Access your favorite games from one cyberpunk command center.">

<!-- firebase-admin.html -->
<meta name="description" content="32Gamers admin panel - manage gaming apps in your portal catalog.">
```

## Social Sharing Optimization

### WARNING: Missing Open Graph Tags

**Detected:** No Open Graph or Twitter Card meta tags.

**Impact:** Social shares will display generic previews instead of branded content.

### Recommended Open Graph Implementation

```html
<!-- index.html - Add to <head> -->
<meta property="og:title" content="32GAMERS // MISSION CONTROL">
<meta property="og:description" content="Your cyberpunk command center for browser games">
<meta property="og:image" content="https://yoursite.com/assets/images/32Gamers_logo.png">
<meta property="og:url" content="https://yoursite.com/">
<meta property="og:type" content="website">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="32GAMERS // MISSION CONTROL">
<meta name="twitter:description" content="Your cyberpunk command center for browser games">
<meta name="twitter:image" content="https://yoursite.com/assets/images/32Gamers_logo.png">
```

## Portal Discovery Flow

### App Names and Descriptions

App metadata in Firestore drives discoverability:

```javascript
// scripts/app.js:29-34
firebaseApps.push({
    id: app.appId,
    name: app.name,
    url: app.url,
    image: app.image,
    description: app.description
});
```

### DO: Write Searchable Descriptions

```javascript
// Admin form - use descriptive content
{
    name: "Space Invaders",
    description: "Classic arcade shooter - defend Earth from alien waves"
}
```

### DON'T: Generic Descriptions

```javascript
// Unhelpful for search
{
    name: "Game 1",
    description: "A fun game"
}
```

## Favicon Implementation

```html
<!-- index.html:7 -->
<link rel="icon" type="image/png" href="assets/favicons/32gamers_favicon.png">
```

### Missing: Apple Touch Icons

```html
<!-- Recommended additions -->
<link rel="apple-touch-icon" sizes="180x180" href="assets/favicons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicons/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicons/favicon-16x16.png">
```

## Canonical URLs

### WARNING: Missing Canonical Tags

**Detected:** No canonical URL tags.

**Recommended:**

```html
<!-- index.html -->
<link rel="canonical" href="https://yoursite.com/">

<!-- firebase-admin.html -->
<link rel="canonical" href="https://yoursite.com/firebase-admin.html">