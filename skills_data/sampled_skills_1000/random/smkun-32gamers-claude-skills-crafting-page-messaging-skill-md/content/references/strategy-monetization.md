# Strategy and Monetization Reference

## Contents
- Current Business Model
- Monetization Opportunities
- Premium Feature Messaging
- Upgrade Flow Patterns

## Current Business Model

The 32Gamers portal is a **free gaming hub** with no current monetization. It serves as a centralized launcher for browser games and apps.

### Value Proposition

```
Current: Free portal → App discovery → Engagement

Missing: Conversion to revenue
```

## Monetization Opportunities

### Option 1: Featured App Placements

App developers pay for premium positioning.

**Messaging approach:**

```html
<!-- Featured badge on app cards -->
<div class="featured-badge">⭐ FEATURED</div>

<!-- Admin form addition -->
<div class="form-group">
    <label for="featured">Featured Placement:</label>
    <select id="featured">
        <option value="false">Standard</option>
        <option value="true">Featured (Premium)</option>
    </select>
</div>
```

### Option 2: Premium Portal Themes

Users unlock additional visual themes.

**Messaging for upgrade CTA:**

```html
<div class="theme-upgrade-prompt">
    <h4>UNLOCK MORE THEMES</h4>
    <p>Customize your command center with premium visual modes</p>
    <button class="btn-premium">Upgrade to Premium</button>
</div>
```

### Option 3: Ad-Supported Free Tier

Non-intrusive ads fund the platform.

**Messaging around ads:**

```html
<!-- Transparent messaging -->
<div class="ad-notice">
    This portal is free thanks to our sponsors
</div>
```

## Premium Feature Messaging

### Value-First Framing

```html
<!-- GOOD - Focus on benefit -->
<h3>Go Premium</h3>
<p>Remove ads, unlock themes, and support development</p>

<!-- BAD - Focus on restriction -->
<h3>Upgrade Required</h3>
<p>This feature is only for premium users</p>
```

### Pricing Page Copy Patterns

```html
<div class="pricing-tier free">
    <h4>FREE</h4>
    <p class="price">$0</p>
    <ul>
        <li>✓ Access all apps</li>
        <li>✓ Search functionality</li>
        <li>✓ Keyboard shortcuts</li>
        <li>○ Standard theme only</li>
    </ul>
</div>

<div class="pricing-tier premium">
    <h4>PREMIUM</h4>
    <p class="price">$5/mo</p>
    <ul>
        <li>✓ Everything in Free</li>
        <li>✓ 10+ visual themes</li>
        <li>✓ Ad-free experience</li>
        <li>✓ Early access to new apps</li>
    </ul>
    <button class="btn-premium">Activate Premium</button>
</div>
```

## Upgrade Flow Patterns

### Soft Gate Pattern

User can still access content but sees upgrade prompt.

```javascript
// Show upgrade prompt on theme selection
function selectTheme(themeId) {
    if (isPremiumTheme(themeId) && !isPremiumUser()) {
        showUpgradePrompt({
            title: 'PREMIUM THEME',
            message: `${themeName} is a premium theme. Upgrade to unlock all visual modes.`,
            cta: 'Unlock Premium Themes'
        });
        return;
    }
    applyTheme(themeId);
}
```

### Hard Gate Pattern

Feature completely blocked without upgrade.

```javascript
// Block feature access
function accessPremiumFeature() {
    if (!isPremiumUser()) {
        window.location.href = '/upgrade.html';
        return;
    }
    // Feature code
}
```

### Upgrade Prompt Messaging

```javascript
function showUpgradePrompt(config) {
    const modal = document.createElement('div');
    modal.className = 'upgrade-modal';
    modal.innerHTML = `
        <div class="upgrade-content">
            <h3>${config.title}</h3>
            <p>${config.message}</p>
            <div class="upgrade-actions">
                <button class="btn-primary">${config.cta}</button>
                <button class="btn-secondary">Maybe Later</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}
```

## Donation Model Alternative

For community-focused projects, donations may be more appropriate than subscriptions.

```html
<div class="support-prompt">
    <h4>Support 32Gamers</h4>
    <p>Enjoying the portal? Help keep the servers running.</p>
    <a href="https://ko-fi.com/32gamers" class="btn-secondary">
        ☕ Buy us a coffee
    </a>
</div>
```

**Placement:** Footer or dedicated support page, not blocking content.