# Growth Engineering Reference

## Contents
- Viral Loop Opportunities
- Referral Mechanisms
- Engagement Hooks
- Retention Messaging

## Viral Loop Opportunities

The 32Gamers portal has limited viral mechanics. Key opportunities exist in share functionality.

### WARNING: No Share Functionality

**Detected:** No social sharing or invite mechanisms in the codebase.

**Impact:** Users cannot easily share apps or invite others.

### Recommended: App Share CTA

```javascript
// Add to scripts/app.js createAppButton method
const shareButton = document.createElement('button');
shareButton.className = 'share-btn';
shareButton.innerHTML = '🔗';
shareButton.title = 'Share this app';
shareButton.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    this.shareApp(app);
});

shareApp(app) {
    const shareUrl = `${window.location.origin}?app=${app.id}`;
    const shareText = `Check out ${app.name} on 32Gamers!`;

    if (navigator.share) {
        navigator.share({
            title: app.name,
            text: shareText,
            url: shareUrl
        });
    } else {
        navigator.clipboard.writeText(shareUrl);
        // Show toast: "Link copied!"
    }
}
```

### Share Message Copy

```javascript
// Themed share messages
const shareMessages = {
    default: `🎮 Check out ${app.name} on 32Gamers // MISSION CONTROL`,
    twitter: `Found this on @32Gamers: ${app.name} 🕹️`,
    email: `Hey! Thought you'd like this game: ${app.name}\n\n${app.description}\n\nPlay it: ${shareUrl}`
};
```

## Engagement Hooks

### Keyboard Shortcuts as Power-User Hooks

```javascript
// Current shortcuts in scripts/app.js
'Ctrl+Alt+A' // Admin access
'Ctrl+F'      // Search

// Missing: Discoverability
```

### Recommended: Keyboard Shortcut Discovery

```html
<!-- Add help hint to footer -->
<div class="shortcuts-hint">
    Press <kbd>?</kbd> for keyboard shortcuts
</div>
```

```javascript
// Add shortcut help modal
document.addEventListener('keydown', (e) => {
    if (e.key === '?') {
        showShortcutsModal();
    }
});

function showShortcutsModal() {
    // Display available shortcuts
    // This creates "aha moment" for power users
}
```

For complete onboarding patterns, see the **designing-onboarding-paths** skill.

## Retention Messaging

### Return Visit Recognition

```javascript
// Detect returning users
const visitCount = parseInt(localStorage.getItem('visit_count') || '0') + 1;
localStorage.setItem('visit_count', visitCount.toString());

// Personalize greeting for returning users
if (visitCount > 1) {
    document.querySelector('.subtitle').textContent = '// WELCOME BACK, OPERATOR';
}
```

### Last Visited App

```javascript
// Track last clicked app
trackAppClick(appId, appName) {
    localStorage.setItem('last_app', JSON.stringify({ id: appId, name: appName }));
    // ... existing tracking
}

// On return, highlight last visited
const lastApp = JSON.parse(localStorage.getItem('last_app'));
if (lastApp) {
    const lastAppCard = document.querySelector(`[data-app-id="${lastApp.id}"]`);
    if (lastAppCard) {
        lastAppCard.classList.add('recently-played');
    }
}
```

## Notification Opportunities

### Browser Notifications for New Apps

```javascript
// Request permission on admin login (high intent moment)
async function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            gtag('event', 'notification_permission', { granted: true });
        }
    }
}

// Notify when new apps are added (requires service worker)
function notifyNewApp(appName) {
    if (Notification.permission === 'granted') {
        new Notification('32Gamers', {
            body: `New mission available: ${appName}`,
            icon: 'assets/favicons/32gamers_favicon.png'
        });
    }
}