---
name: tailwind-patterns
description: Best practices for utility-first styling with Tailwind CSS. Responsive design, dark mode, and design system continuity.
---

# Tailwind CSS Patterns

Maintain a clean, scalable utility-first codebase.

## 1. Responsive Design
- **Mobile First:** Always write base classes for mobile, then use prefixes (`sm:`, `md:`, `lg:`) for larger screens.
- **Pattern:** `class="w-full md:w-1/2 lg:w-1/3"`.

## 2. Component Extraction
- **When:** If a pattern repeats 3+ times OR exceeds 10+ utilities.
- **How:** Create a React component rather than using `@apply` in CSS.

## 3. Design System Continuity
- **Spacing:** Use the standard scale (`p-4`, `m-2`) instead of arbitrary values (`p-[17px]`).
- **Colors:** Use theme tokens (`text-primary`, `bg-surface`) instead of hex codes.

## 4. Dark Mode
- **Strategy:** Use the `dark:` prefix for all theme-sensitive colors.
- **Check:** Always verify contrast in both light and dark modes.

## 5. Class Ordering
- Recommended order: Positioning → Box Model → Typography → Visual → Misc.
- (Automatic ordering via Prettier plugin is preferred).
