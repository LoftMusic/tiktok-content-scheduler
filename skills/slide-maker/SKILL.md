---
name: slide-maker
description: >
  Generate professional presentation slides and visual infographics for YouTube
  videos, talks, and content. Use when the user says "make slides", "create visuals",
  "presentation images", "infographic", "slides for my video", or needs visual aids
  for content.
---

# Slide Maker -- Presentation Visual Generator

Create stunning dark-theme presentation slides using AI image generation. Optimized for YouTube videos, screen shares, and content creation.

## Design System

Every slide follows this consistent brand:

### Colors
- **Background:** #0A0A12 (near-black)
- **Primary text:** White (#FFFFFF) bold
- **Green (positive/good):** #10b981
- **Red (negative/bad):** #EF4444
- **Cyan (info/neutral):** #06b6d4
- **Purple (feature/highlight):** #8b5cf6
- **Orange (action/energy):** #f97316
- **Yellow (warning/attention):** #FFD93D

### Style Rules
- Dark tech aesthetic -- minimal, professional, modern
- Large bold headlines -- readable at YouTube 1080p AND mobile
- Strong visual metaphors (chaos vs order, before/after, big vs small)
- Color-coded meaning: green = good, red = bad, always
- No people, no faces, no photographs
- No clutter -- every element earns its place
- Generous negative space
- Punchy tagline/subtitle at the bottom of every slide

### Typography
- Headlines: Large, bold, white
- Numbers/labels: Extra bold, colored to match theme
- Subtitles: Medium weight, slightly dimmer
- Fine print: AVOID -- if you can't read it on a phone, don't include it

## Slide Types

### 1. Numbered Point Slide
For "4 reasons why..." or "5 steps to..." series.

Structure:
- Top: "WHY [TOPIC] MATTERS" or similar title
- Large colored number + keyword (e.g., "1 CONSISTENCY")
- Visual metaphor in the center
- Tagline at bottom in quotes

### 2. Before/After Comparison
For showing transformation or improvement.

Structure:
- Left side: "WITHOUT [thing]" -- red tones, messy/chaotic visuals, red X
- Right side: "WITH [thing]" -- green tones, clean/organized visuals, green checkmark
- Clear divider between sides

### 3. Data Visualization
For stats, metrics, comparisons.

Structure:
- Large numbers as the hero element
- Comparison bars (big red bar vs small green bar)
- Arrows showing direction (savings, growth, reduction)
- Keep to 2-3 data points max per slide

### 4. Process Flow
For showing workflows or step sequences.

Structure:
- Steps connected by arrows or a timeline
- Each step has an icon and short label
- Highlight the current/key step with a glow effect
- Max 4-5 steps per slide

### 5. Quote/Statement Slide
For key takeaways or memorable lines.

Structure:
- Large quote text centered
- Attribution or context below
- Subtle background glow or accent

### 6. Title Card
For section headers in longer presentations.

Structure:
- Big bold title centered
- Optional subtitle
- Accent glow behind text

## Generation Process

1. **Understand the content** -- What point is the slide making?
2. **Choose slide type** -- Which type above fits best?
3. **Write the prompt** -- Include:
 - Dark background (#0A0A12) always
 - Specific colors from the palette
 - The exact text to display
 - Visual metaphor description
 - "Minimal, professional dark tech aesthetic. No people no faces."
 - Resolution: 1K for standard, 2K for hero/thumbnail images
4. **Generate** using your preferred AI image generation tool (e.g., nano-banana-pro, DALL-E, Midjourney)
5. **Review** -- Check readability and visual clarity
6. **Iterate** if needed -- Regenerate with adjusted prompt

## Naming Convention

Save slides as:
- Series: `slide-[topic]-[number].png` (e.g., `slide-skills-1.png`)
- Standalone: `slide-[topic].png` (e.g., `slide-token-savings.png`)

## Multi-Slide Series

When creating a series (e.g., "4 reasons why skills matter"):
1. Plan ALL slides first -- ensure visual consistency
2. Use the same title across all slides
3. Number each slide with a different accent color
4. Each slide gets ONE key point -- don't cram
5. Send slides one at a time with captions

## Quality Checklist

Before delivering any slide:
- [ ] Readable at 1080p YouTube embed size?
- [ ] Readable on mobile (small screen)?
- [ ] Clear visual metaphor -- point understood in 2 seconds?
- [ ] Consistent with dark theme brand?
- [ ] Tagline is punchy and memorable?
- [ ] No excessive fine text or clutter?

## Rules

- Always use the dark theme (#0A0A12 background) -- never white/light backgrounds
- **Always landscape (16:9 widescreen)** -- include "LANDSCAPE orientation (16:9 widescreen)" in every prompt. Never portrait.
- Never include people or faces in slides
- Max 10-15 words of visible text per slide (excluding fine labels)
- If the user asks for "slides about X" without specifics, propose the slide topics first before generating
