---
name: tailwind-v4-shadcn
description: >
  Tailwind v4 + shadcn/ui component library.
---

# Tailwind v4 + shadcn/ui

## Setup
```bash
npx shadcn@latest init # scaffolds components.json + globals.css
npx shadcn@latest add button dialog card # add components
```

## Tailwind v4 Changes
- CSS-first config: tokens in `@theme` blocks inside CSS, not JS config
- No `tailwind.config.js` needed — use `@import "tailwindcss"`
- Automatic content detection (no `content` array)
- Native CSS nesting + `@variant` directive

## shadcn/ui Patterns
- Components live in `src/components/ui/` — you OWN the code (not a dependency)
- Customize by editing the file directly
- Uses Radix UI primitives under the hood for accessibility
- `cn()` helper (clsx + tailwind-merge) for class composition

## Key Components
- **Button:** `<Button variant="destructive" size="sm">Delete</Button>`
- **Dialog:** Radix-based modal with `DialogTrigger`, `DialogContent`
- **Form:** React Hook Form + Zod validation integration
- **DataTable:** TanStack Table wrapper with sorting, filtering, pagination

## Tips
- Use CSS variables for theming: `--primary`, `--background`, etc.
- Dark mode via `class` strategy + `next-themes`
- Check https://ui.shadcn.com for full component catalog
