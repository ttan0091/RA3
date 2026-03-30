# Measurement and Testing Reference

## Contents
- Analytics Implementation
- Conversion Event Tracking
- A/B Testing Messaging
- Copy Performance Metrics

## Analytics Implementation

### Current Tracking Setup

```javascript
// scripts/app.js:94-102
trackAppClick(appId, appName) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'app_click', {
            'app_id': appId,
            'app_name': appName
        });
    }
}
```

**Status:** Basic gtag integration exists but Google Analytics is not loaded in the HTML.

### WARNING: Incomplete Analytics Setup

**Detected:** `gtag` is referenced but no Google Analytics script tag in HTML files.

**Impact:** Click tracking code exists but doesn't fire.

### Recommended Implementation

```html
<!-- Add to index.html <head> before other scripts -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Conversion Event Tracking

### Key Events to Track

| Event | Trigger | Purpose |
|-------|---------|---------|
| `app_click` | User clicks app card | Engagement |
| `admin_access` | User enters admin | Power user |
| `admin_login` | Successful OAuth | Admin funnel |
| `app_added` | New app created | Content growth |
| `search_used` | User searches | Discovery |

### Implementing Missing Events

```javascript
// Add to firebase-admin.html after successful login
gtag('event', 'admin_login', {
    'method': 'google'
});

// Add after successful app creation
gtag('event', 'app_added', {
    'app_id': newApp.appId,
    'app_name': newApp.name
});

// Add to search functionality in scripts/app.js
gtag('event', 'search', {
    'search_term': searchTerm
});
```

## A/B Testing Messaging

### Testing Framework Options

For a static site on ifastnet, client-side A/B testing is the primary option.

### Simple A/B Test Pattern

```javascript
// Add to scripts/app.js
function getVariant(testName) {
    const stored = localStorage.getItem(`ab_${testName}`);
    if (stored) return stored;

    const variant = Math.random() < 0.5 ? 'A' : 'B';
    localStorage.setItem(`ab_${testName}`, variant);
    return variant;
}

// Usage for headline test
const headlineVariant = getVariant('headline');
if (headlineVariant === 'B') {
    document.querySelector('.cyber-title .glitch').textContent = 'COMMAND CENTER';
    document.querySelector('.cyber-title .glitch').dataset.text = 'COMMAND CENTER';
}
```

### Tracking Variant Performance

```javascript
// Track which variant user saw
gtag('event', 'experiment_impression', {
    'experiment_id': 'headline_test',
    'variant_id': headlineVariant
});
```

## Copy Performance Metrics

### What to Measure

| Metric | Indicates | How to Track |
|--------|-----------|--------------|
| App click rate | Card copy effectiveness | `app_click` events / pageviews |
| Admin conversion | Login copy clarity | `admin_login` / `admin_access` |
| Search usage | Discovery needs | `search` events |
| Error recovery | Error copy clarity | Retry clicks after errors |

### Creating a Messaging Report

```javascript
// Console snippet to audit current messaging
document.querySelectorAll('[title], [placeholder], [aria-label]').forEach(el => {
    console.log({
        element: el.tagName,
        title: el.title,
        placeholder: el.placeholder,
        ariaLabel: el.getAttribute('aria-label')
    });
});
```

For detailed analytics patterns, see the **instrumenting-product-metrics** skill.