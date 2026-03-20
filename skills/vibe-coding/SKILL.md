---
name: vibe-coding
description: >
  Build and ship software through conversation, screenshots, and autonomous visual QA.
  Use when you want to build features, fix UI, audit an app, deploy, or iterate on
  any project. Triggers on "build this", "fix this", "audit it", "ship it", "vibe code".
---

# Vibe Code Like a Legend

_See it. Build it. Audit it. Ship it. One cycle._

## The Philosophy

You describe what you want in plain English + screenshots. Your agent codes it, deploys it, and verifies visually. No IDE needed. No back-and-forth. Just results.

---

## Communication Protocol

### Your Commands
- **"Show me [page]"** -- Screenshot that page and share it
- **"Fix [description]"** -- Find and fix the issue
- **"Change [what] to [what]"** -- Precision edit
- **"Deploy" / "Ship it"** -- Push to production, send link after
- **"Audit [page/app]"** -- Screenshot every page, list all issues
- **"Vibe code like a legend"** -- Full scan > audit > build > ship cycle
- **"Love it"** -- Move on
- **"Not feeling it"** -- Try a different approach
- **"Close but [tweak]"** -- Iterate on current version
- **Screenshot + description** -- Most common and most effective

---

## The Legend Cycle (Full Audit Mode)

Triggered by: "audit it", "clean it up", "make it look good", "vibe code legend mode", "ship it clean"

### Phase 1: SCAN
1. Open every page of the app in the browser tool
2. Screenshot each page (desktop + mobile viewport)
3. Read the code for each page to understand structure
4. Build a comprehensive punch list organized by priority

### Phase 2: AUDIT
Present findings as a clean punch list:
- Page-by-page breakdown
- Severity: RED broken, YELLOW ugly/janky, GREEN polish/nice-to-have
- Screenshots attached where helpful
- Estimated scope (quick fix vs rebuild)

### Phase 3: BUILD
After approval (or "do that"):
1. Spawn a coding agent with a detailed task brief covering ALL fixes
2. Brief includes: exact file paths, design system rules, what to change and why
3. Agent batches everything into minimal commits
4. Agent pushes to GitHub when done

### Phase 4: SHIP
1. Deploy to hosting (Vercel, here.now, etc.)
2. Verify build succeeds
3. Screenshot the live result (desktop + mobile)
4. Send the live link
5. Done. One cycle.

---

## Workflow Rules

1. **Batch changes** -- collect multiple fixes, deploy once (unless urgent)
2. **Screenshot before/after** -- verify visually using browser tool
3. **Always send the link** after every deploy
4. **Proactively fix** obvious issues spotted during screenshots
5. **Commit with descriptive messages** so git history is clean
6. **Never break what's working** -- check build before deploying
7. **One deploy per round** -- not per individual fix

---

## Model Strategy (Cost Optimization)

**Main agent (direct):** Quick fixes, iteration, back-and-forth
**Coding agent (sub-agent):** Big builds, feature work, refactors

Use a cheaper model (like Sonnet) for coding sub-agents. Escalate to a more powerful model only if the sub-agent fails twice or the architecture is complex.

---

## Coding Agent Task Brief Template

Always include:
1. Full file paths for every file that needs changes
2. Design system rules (colors, fonts, spacing)
3. Specific before/after descriptions for each fix
4. "Commit with descriptive messages and push to origin main."
5. "Test that build compiles. No broken imports or type errors."

---

## Universal Design Rules

- **NO EMOJIS in UI** -- use proper SVG icon libraries (Lucide React preferred)
- Icons > emojis. Always. Professional-grade aesthetic.
- Default icon library: **Lucide React** (`lucide-react`) -- clean, 1px stroke
- Mobile-first responsive design on everything
- "Holy shit this is cool" is the bar. If a user wouldn't say that, it's not done.

---

## Deploy Checklist
- [ ] Code changes complete
- [ ] `git add -A && git commit -m "descriptive message"`
- [ ] `git push origin main`
- [ ] Deploy to hosting
- [ ] Build succeeded (no errors)
- [ ] Screenshot landing page (desktop)
- [ ] Screenshot on mobile viewport
- [ ] Send the live link
