---
name: gh-issues
description: >
  Auto-fix GitHub issues with parallel sub-agents. Spawns coding agents to implement
  fixes and open PRs.
---

# gh-issues — Auto-fix GitHub Issues

Orchestrator that fetches GitHub issues, spawns sub-agents to implement fixes, and opens PRs.

## Usage
```
/gh-issues [owner/repo] [flags]
```

## Flags
| Flag | Default | Description |
|------|---------|-------------|
| --label | none | Filter by label (e.g. bug) |
| --limit | 10 | Max issues to fetch |
| --milestone | none | Filter by milestone title |
| --assignee | none | Filter by assignee (@me for self) |
| --state | open | Issue state: open/closed/all |
| --fork | none | Your fork (user/repo) for PRs |
| --watch | false | Keep polling for new issues |
| --interval | 5 | Minutes between polls (with --watch) |
| --dry-run | false | Fetch and display only |
| --yes | false | Skip confirmation |
| --reviews-only | false | Only check PRs for review comments |
| --cron | false | Fire-and-forget mode |
| --model | none | Model for sub-agents |
| --notify-channel | none | Telegram channel for PR notifications |

## Workflow (6 Phases)
1. **Parse Args** — Detect repo from git remote if not specified
2. **Fetch Issues** — GitHub REST API (curl, no gh CLI). Filters out PRs.
3. **Confirm** — Shows table, asks which to process (or auto with --yes)
4. **Pre-flight** — Checks: dirty tree, remote access, token validity, existing PRs/branches
5. **Spawn Agents** — Up to 8 parallel sub-agents. Each: analyzes issue → creates branch → implements fix → runs tests → pushes → opens PR
6. **PR Reviews** — Monitors open PRs for review comments, spawns agents to address feedback

## Key Details
- Uses curl + GitHub REST API (no gh CLI dependency)
- GH_TOKEN from env or `~/.openclaw/openclaw.json` skills config
- Branches: `fix/issue-{N}` from base branch
- Fork mode: push to fork, PR targets upstream
- Cron mode: processes one issue per run, fire-and-forget
- Watch mode: continuous polling with configurable interval
- Claim file prevents duplicate processing across cron runs
