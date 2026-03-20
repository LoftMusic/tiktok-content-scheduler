---
name: tailwind-design-system
description: >
  Tailwind CSS design system patterns and component architecture.
---

# Tailwind Design System

## Design Tokens
Define tokens in `tailwind.config.js` — colors, spacing, typography, shadows.
```js
// tailwind.config.js
module.exports = {
 theme: {
 extend: {
 colors: { brand: { 50: '#f0f9ff', 500: '#3b82f6', 900: '#1e3a5f' } },
 spacing: { 18: '4.5rem' },
 fontSize: { '2xs': '0.625rem' },
 }
 }
}
```

## Component Patterns
- **Utility-first:** Compose classes, extract components only when repeated 3+ times.
- **@apply sparingly:** Use in base layers or component libraries, not app code.
- **Variants:** Group hover/focus/dark states: `hover:bg-brand-500 focus:ring-2 dark:bg-gray-800`
- **Responsive:** Mobile-first breakpoints: `text-sm md:text-base lg:text-lg`

## Architecture
- Atomic components (Button, Input, Badge) → Molecules (SearchBar, Card) → Organisms (Navbar, Hero)
- Use `cn()` utility (clsx + twMerge) for conditional + override-safe classes
- Keep `@layer base`, `@layer components`, `@layer utilities` organized

## Tips
- Use `prose` for content typography (`@tailwindcss/typography`)
- `container mx-auto px-4` for consistent layouts
- Prefer `gap-*` over margins in flex/grid
