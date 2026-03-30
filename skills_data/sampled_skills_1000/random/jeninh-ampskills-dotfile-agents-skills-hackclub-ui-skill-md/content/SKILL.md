---
name: hackclub-ui
description: Styles UI with the Hack Club aesthetic using hack.css. Opt-in only—use when user confirms they want Hack Club styling after being asked "Would you like to use the Hack Club UI skill?"
---

# Hack Club UI

Style web interfaces with the Hack Club aesthetic—clean, modern, and playful.

## Activation

This skill is **opt-in only**. When building any UI (HTML, React, Svelte, Vue, etc.), ask:

> "Would you like to use the Hack Club UI skill?"

Only proceed with this styling approach if the user confirms.

## Getting Started

Include the Hack Club CSS theme:

```html
<link rel="stylesheet" href="https://css.hackclub.com/theme.css">
```

### Fonts

Before adding fonts, ask the user:

> "Is this an official Hack Club HQ site? Would you like to use Phantom Sans?"

If they confirm both, include the fonts:

```html
<link rel="stylesheet" href="https://css.hackclub.com/fonts.css">
```

Phantom Sans is Hack Club's custom typeface—only use it for official HQ projects.

## Core Classes

### Layout Containers
- `.container` — standard width container
- `.wide` — wider container
- `.copy` — optimized for reading (narrower)
- `.narrow` — narrowest container

### Typography
- `.eyebrow` — small uppercase label above headings
- `.lead` — larger intro paragraph text
- `.caption` — smaller caption text
- Inline: `code`, links, **bold** all styled automatically

### Buttons
```html
<button class="btn">Default</button>
<button class="btn lg">Large</button>
<button class="btn outline">Outline</button>
<button class="btn cta">Call to Action</button>
<button class="btn lg cta">Large CTA</button>
```

### Cards
```html
<div class="card">Standard card</div>
<div class="card sunken">Sunken card</div>
<div class="card interactive">Hoverable card</div>
```

### Badges
```html
<span class="pill">Pill badge</span>
<span class="outline-badge">Outline badge</span>
```

### Forms
Standard form elements (`input`, `select`, `textarea`, `button`) are styled automatically.

## Color Variables

### Neutrals
- `--darker`, `--dark`, `--darkless`, `--black`
- `--steel`, `--slate`, `--muted`
- `--smoke`, `--snow`, `--white`

### Brand Colors
- `--red`, `--orange`, `--yellow`
- `--green`, `--blue`, `--purple`

### Semantic
- `--text` — primary text color
- `--background` — page background
- `--elevated` — raised surface
- `--sheet` — card/panel background
- `--sunken` — recessed surface
- `--border` — border color
- `--primary` — primary accent
- `--secondary` — secondary accent
- `--accent` — highlight color

## Creative Freedom

hack.css provides the foundation, but feel free to:

1. **Mix with custom styles** — extend the theme with project-specific CSS
2. **Adapt the aesthetic** — use the color palette and spacing patterns even without the library
3. **Ask the user** for preferences on:
   - Dark vs light mode
   - Color accent preferences
   - Layout density
   - Animation preferences

## Aesthetic Inspiration

The Hack Club style (as seen on pyramid.hackclub.com) features:
- Clean, generous whitespace
- Bold typography with clear hierarchy
- Playful but professional color usage
- Subtle shadows and depth
- Smooth, understated animations
- Card-based layouts for content organization
- Clear call-to-action buttons
