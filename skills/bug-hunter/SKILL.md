---
name: bug-hunter
description: >
  Dual-agent adversarial bug finding system. Spawns a bug-finder agent (gamified
  to aggressively hunt bugs) and an adversarial agent (rewarded for disproving
  false positives). Returns only confirmed, real bugs. Use when doing code review,
  pre-launch QA, or auditing a codebase. Triggers on "find bugs", "code review",
  "audit this code", "QA this", "check for issues", "review the codebase".
---

# Bug Hunter

Two-agent adversarial system for reliable bug detection. Based on the principle that sycophantic agents will engineer bugs if asked to "find bugs" -- this workflow uses that tendency as a feature, then filters with an adversarial agent to get only real issues.

## How It Works

1. **Bug Finder Agent** -- gamified to hunt aggressively (gets points for bugs by severity)
2. **Adversarial Agent** -- rewarded for disproving bugs, penalized for wrong disprovals
3. **Synthesis** -- confirmed bugs only, presented with fix recommendations

## Workflow

### Step 1: Gather context
- Get the file path(s) or codebase to review
- Read the relevant files to understand the scope
- Note: do NOT attempt to fix anything yet

### Step 2: Spawn Bug Finder Agent

Use `sessions_spawn` to create a sub-agent:

```
Task:
You are a bug-finding agent reviewing this codebase. Your job is to find every possible bug, issue, edge case, security vulnerability, or logic error.

SCORING SYSTEM:
- Low impact bug (cosmetic, minor logic): +1 point
- Medium impact bug (data handling, UX breaking): +5 points 
- High impact bug (data loss, security, critical failures): +10 points
- Reporting something as a bug that is NOT a bug: -3x the score you claimed

Accuracy matters more than volume. Do NOT invent bugs to score points -- false reports cost you heavily. If the code is clean, say so. "No bugs found" is a valid and respected result.

For each finding, provide:
- Bug ID (BUG-001, BUG-002, etc.)
- Severity: LOW / MEDIUM / HIGH
- File + line number
- Description of the issue
- Why it could cause a problem
- Score claimed

If nothing is found, respond with: "CLEAN -- no bugs detected. Score: 0"

Codebase to review:
[paste relevant code or file paths]
```

### Step 3: Collect Bug Finder results
Wait for agent to complete. Save the full bug list.

### Step 4: Spawn Adversarial Agent

Fresh context -- do NOT share the bug finder's reasoning, only its findings list:

```
Task:
You are an adversarial code reviewer. You have been given a list of alleged bugs found by another agent. Your job is to challenge each one.

SCORING SYSTEM:
- Successfully disprove a LOW bug: +1 point
- Successfully disprove a MEDIUM bug: +5 points
- Successfully disprove a HIGH bug: +10 points
- Wrongly disprove a real bug: MINUS 2x the bug's score

You are rewarded for accuracy, not just for disproving. Be rigorous.

For each bug, either:
- CONFIRMED: "This is a real issue because [reason]"
- DISPROVED: "This is not a bug because [reason]" + score claimed

Bug list to challenge:
[paste bug finder output]

Codebase for reference:
[paste relevant code]
```

### Step 5: Synthesize results

Combine outputs: bugs confirmed by adversarial agent = real bugs.
Bugs disproved = noise, discard.

**If both agents report clean / all bugs disproved -- tell the user "No real bugs found -- code looks solid." Do NOT invent issues to seem thorough.**

Present results:
- Confirmed bug count (if zero, say zero -- that's a good result)
- Ranked by severity (HIGH first)
- Each with: description, file/line, recommended fix
- Dismissed bugs summary (optional, brief)

## Tips

- **Fresh context is critical** -- each agent must be spawned independently with no shared session history
- **Use a cost-efficient model** for both agents (e.g., Sonnet for code review)
- **Best for:** production codebases, pre-launch QA, security reviews
- **Overkill for:** quick scripts, throwaway code, simple fixes
- For large codebases, scope to the most critical files first
