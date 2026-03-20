---
name: web-design-guidelines
description: >
  General web design best practices.
---

# Web Design Guidelines

## Layout
- **Max content width:** 1200-1440px with centered container
- **Grid:** CSS Grid for page layout, Flexbox for component layout
- **Spacing scale:** Use consistent multipliers (4px/8px base)
- **Whitespace:** More is almost always better — let content breathe

## Typography
- Limit to 2 fonts max (1 heading + 1 body)
- Body: 16-18px minimum, line-height 1.5-1.7
- Heading hierarchy: Clear size/weight contrast between h1-h4
- Max line length: 60-75 characters for readability

## Color
- 60-30-10 rule: 60% dominant, 30% secondary, 10% accent
- Contrast ratio: 4.5:1 minimum (WCAG AA) for text
- Use color meaningfully — don't rely on color alone for info

## Responsive
- Mobile-first: Design smallest screen first, enhance upward
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Touch targets: 44×44px minimum on mobile
- Test on real devices — not just browser DevTools

## Performance
- Images: WebP/AVIF, lazy loading, explicit width/height
- Fonts: `font-display: swap`, preload critical fonts
- Above-the-fold content should load in <1.5s
- Core Web Vitals: LCP<2.5s, CLS<0.1, INP<200ms

## Accessibility
- Semantic HTML: `<nav>`, `<main>`, `<article>`, `<button>`
- Alt text on all images, labels on all form inputs
- Keyboard navigable: focus styles, tab order, skip links
- Screen reader testing: VoiceOver (Mac), NVDA (Windows)

## Tips
- Consistent spacing > pixel-perfect design
- Progressive disclosure: don't show everything at once
- Loading states for every async action
- Error states that explain AND help fix the problem
