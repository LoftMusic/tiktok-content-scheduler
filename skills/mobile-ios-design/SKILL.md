---
name: mobile-ios-design
description: >
  iOS design patterns and Human Interface Guidelines.
---

# iOS Design (HIG)

## Core Principles
- **Clarity:** Content is king. Text readable at every size. Icons precise and clear.
- **Deference:** UI helps people understand content, never competes with it.
- **Depth:** Visual layers and motion provide hierarchy and context.

## Navigation Patterns
- **Tab Bar:** 3-5 primary destinations (bottom, always visible)
- **Navigation Stack:** Push/pop with back button (hierarchical content)
- **Modal:** Interrupts flow for focused tasks (use sparingly)
- **Sidebar:** iPad/Mac — collapsible primary navigation

## Layout
- Safe areas: Respect notch, home indicator, Dynamic Island
- Standard margins: 16pt (compact), 20pt (regular)
- Touch targets: Minimum 44×44pt
- Use SF Symbols for consistent iconography (5,000+ icons)

## Typography
- San Francisco (SF Pro) system font — scales with Dynamic Type
- Semantic styles: `.largeTitle`, `.headline`, `.body`, `.caption`
- Always support Dynamic Type for accessibility

## Colors & Dark Mode
- Use semantic colors: `.label`, `.secondaryLabel`, `.systemBackground`
- System colors auto-adapt to dark mode
- Provide both light/dark variants for custom colors

## SwiftUI Patterns
- `NavigationStack` + `NavigationLink` for navigation
- `@State`, `@Binding`, `@Observable` for state management
- `.sheet()`, `.alert()`, `.confirmationDialog()` for modals
- Use `.task {}` for async data loading

## Tips
- Haptic feedback: `UIImpactFeedbackGenerator` for physical responses
- Respect user settings: reduce motion, increase contrast, bold text
- App Store review: no private APIs, no misleading metadata
