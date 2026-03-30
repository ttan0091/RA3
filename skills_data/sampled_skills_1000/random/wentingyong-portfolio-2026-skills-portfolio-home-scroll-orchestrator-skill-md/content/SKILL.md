---
name: portfolio-home-scroll-orchestrator
description: Implement Home page scroll choreography with a pinned GSAP timeline orchestrating horizontal hero transitions, About section hold/animation, Projects/Blogs vertical scroll, and CTA. Desktop and mobile fallback behavior included.
---
# SKILL: portfolio-home-scroll-orchestrator

## Intent
Implement the Home page scroll narrative with a single pinned GSAP timeline:
horizontal panels + About hold/animation + Projects/Blogs vertical scroll + CTA.

## Use when
- Implementing Home scroll behavior
- Fixing pinning, transitions, or ScrollTrigger lifecycle issues
- Creating desktop vs mobile fallback behavior

## Required choreography (must match spec)
1) Pin the Home sequence and scrub a single timeline.
2) Hero -> About: horizontal transition (full viewport width).
3) About: hold in place; drive its internal animation via the pinned timeline.
4) About -> Projects: horizontal transition.
5) Projects: vertical scroll through content inside the pinned sequence.
6) Projects -> Blogs: horizontal transition.
7) Blogs: vertical scroll through content inside the pinned sequence.
8) Release pin into CTA after Blogs scroll completes.

## Implementation constraints
- Home orchestration lives in a single Client Component:
  - `HomeExperience.tsx` (or equivalent).
- Use refs for each section + data hooks:
  - data-section="hero|about|projects|blogs|cta".
  - data-anim="about-content" for About animation target.
- Use a single pinned ScrollTrigger timeline tied to a sequence wrapper.
- No "hide the track" tricks; the timeline must remain reversible.
- Use a placeholder constant to tune About scroll length.
- Use `gsap.context()` + ScrollTrigger; clean up on unmount.
- Desktop: enable horizontal/pin choreography.
- Mobile/touch + reduced motion: fall back to normal vertical stack.
- Rebuild on resize and on content height changes (ResizeObserver).

## Agent workflow
1) Inspect DOM structure and section refs
2) Implement a horizontal "track" wrapper for Hero/About/Projects/Blogs panels
3) Add a single pinned timeline on the sequence wrapper:
   - hero -> about (x translate by panel width)
   - about hold/animation (duration = viewport height * multiplier)
   - about -> projects (x translate)
   - projects vertical (y translate by content overflow)
   - projects -> blogs (x translate)
   - blogs vertical (y translate by content overflow)
4) Place CTA after the pinned sequence (normal flow)
5) Add resize + ResizeObserver to rebuild timeline and refresh ScrollTrigger
6) Verify cleanup: kill timeline + ScrollTrigger on unmount

## Acceptance tests
- Smooth scroll (no jitter) on desktop
- No page-level horizontal scrollbar
- Reverse scroll always works (scrubbed timeline is reversible)
- About stays full screen while its animation plays
- Projects and Blogs vertical scroll honor dynamic content height
- Mobile: no horizontal scroll hijacking, normal vertical UX
- prefers-reduced-motion: no pin/horizontal choreography
