---
name: self-improvement
description: >
  Captures learnings, errors, and corrections to enable continuous improvement. Use when:
  (1) A command or operation fails unexpectedly, (2) User corrects the agent,
  (3) User requests a capability that doesn't exist, (4) An external API or tool fails,
  (5) Agent realizes its knowledge is outdated, (6) A better approach is discovered
  for a recurring task.
---

# Self-Improvement Skill

Log learnings and errors to markdown files for continuous improvement. Coding agents can later process these into fixes, and important learnings get promoted to project memory.

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` with category `correction` |
| User wants missing feature | Log to `.learnings/FEATURE_REQUESTS.md` |
| API/external tool fails | Log to `.learnings/ERRORS.md` with integration details |
| Knowledge was outdated | Log to `.learnings/LEARNINGS.md` with category `knowledge_gap` |
| Found better approach | Log to `.learnings/LEARNINGS.md` with category `best_practice` |
| Broadly applicable learning | Promote to `AGENTS.md`, workspace files, or project docs |

## Setup

Create the learnings directory in your workspace:

```bash
mkdir -p ~/.openclaw/workspace/.learnings
```

Then create the log files:
- `LEARNINGS.md` -- corrections, knowledge gaps, best practices
- `ERRORS.md` -- command failures, exceptions
- `FEATURE_REQUESTS.md` -- user-requested capabilities

## Logging Format

### Learning Entry

Append to `.learnings/LEARNINGS.md`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
```

### Error Entry

Append to `.learnings/ERRORS.md`:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending

### Summary
Brief description of what failed

### Error
Actual error message or output

### Context
- Command/operation attempted
- Input or parameters used

### Suggested Fix
If identifiable, what might resolve this
```

### Feature Request Entry

Append to `.learnings/FEATURE_REQUESTS.md`:

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending

### Requested Capability
What the user wanted to do

### User Context
Why they needed it, what problem they're solving

### Suggested Implementation
How this could be built
```

## ID Generation

Format: `TYPE-YYYYMMDD-XXX`
- TYPE: `LRN` (learning), `ERR` (error), `FEAT` (feature)
- YYYYMMDD: Current date
- XXX: Sequential number (e.g., `001`, `002`)

## Promoting to Project Memory

When a learning is broadly applicable (not a one-off fix), promote it to permanent project memory.

### When to Promote
- Learning applies across multiple files/features
- Knowledge any contributor (human or AI) should know
- Prevents recurring mistakes
- Documents project-specific conventions

### Promotion Targets

| Target | What Belongs There |
|--------|-------------------|
| `AGENTS.md` | Agent-specific workflows, tool usage patterns, automation rules |
| `SOUL.md` | Behavioral guidelines, communication style, principles |
| `TOOLS.md` | Tool capabilities, usage patterns, integration gotchas |

### How to Promote
1. **Distill** the learning into a concise rule or fact
2. **Add** to appropriate section in target file
3. **Update** original entry status to `promoted`

## Detection Triggers

Automatically log when you notice:

**Corrections**: "No, that's not right...", "Actually, it should be...", "You're wrong about..."
**Feature Requests**: "Can you also...", "I wish you could...", "Is there a way to..."
**Knowledge Gaps**: User provides information you didn't know, documentation is outdated
**Errors**: Command returns non-zero exit code, exception or stack trace, unexpected output

## Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| `critical` | Blocks core functionality, data loss risk, security issue |
| `high` | Significant impact, affects common workflows, recurring issue |
| `medium` | Moderate impact, workaround exists |
| `low` | Minor inconvenience, edge case, nice-to-have |

## Periodic Review

Review `.learnings/` at natural breakpoints:
- Before starting a new major task
- After completing a feature
- When working in an area with past learnings

```bash
# Count pending items
grep -h "Status**: pending" .learnings/*.md | wc -l

# List high-priority items
grep -B5 "Priority**: high" .learnings/*.md | grep "^## \["
```

## Best Practices

1. **Log immediately** -- context is freshest right after the issue
2. **Be specific** -- future agents need to understand quickly
3. **Include reproduction steps** -- especially for errors
4. **Link related files** -- makes fixes easier
5. **Suggest concrete fixes** -- not just "investigate"
6. **Promote aggressively** -- if in doubt, add to project docs
7. **Review regularly** -- stale learnings lose value
