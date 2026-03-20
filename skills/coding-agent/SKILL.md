---
name: coding-agent
description: >
  Delegate coding tasks to Codex, Claude Code, or Pi agents via background
  process. Use when building/creating new features or apps, reviewing PRs,
  refactoring large codebases, or iterative coding that needs file exploration.
  NOT for simple one-liner fixes (just edit) or reading code (use read tool).
  Claude Code uses --print --permission-mode bypassPermissions (no PTY).
  Codex/Pi/OpenCode require pty:true.
---

# Coding Agent (bash-first)

Use bash (with optional background mode) for all coding agent work.

## PTY Mode: Codex/Pi/OpenCode yes, Claude Code no

For Codex, Pi, and OpenCode, PTY is required (interactive terminal apps):
```bash
# Correct for Codex/Pi/OpenCode
exec pty:true command:"codex exec 'Your prompt'"
```

For Claude Code, use --print --permission-mode bypassPermissions instead:
```bash
# Correct for Claude Code (no PTY needed)
cd /path/to/project && claude --permission-mode bypassPermissions --print 'Your task'
```

## Quick Start: One-Shot Tasks

```bash
# Quick chat (Codex needs a git repo!)
SCRATCH=$(mktemp -d) && cd $SCRATCH && git init && codex exec "Your prompt here"

# Or in a real project with PTY
exec pty:true workdir:~/Projects/myproject command:"codex exec 'Add error handling'"
```

## Background Mode for Longer Tasks

```bash
# Start agent in background
exec pty:true workdir:~/project background:true command:"codex exec --full-auto 'Build a snake game'"

# Monitor progress
process action:log sessionId:XXX

# Check if done
process action:poll sessionId:XXX

# Kill if needed
process action:kill sessionId:XXX
```

## Codex CLI Flags
- exec "prompt" -- One-shot execution, exits when done
- --full-auto -- Sandboxed but auto-approves in workspace
- --yolo -- NO sandbox, NO approvals (fastest, most dangerous)

## Claude Code
```bash
# Foreground
exec workdir:~/project command:"claude --permission-mode bypassPermissions --print 'Your task'"

# Background
exec workdir:~/project background:true command:"claude --permission-mode bypassPermissions --print 'Your task'"
```

## Key Tips
- workdir matters: Agent wakes up focused in the right directory
- Always use PTY for Codex/Pi/OpenCode, never for Claude Code
- For PR reviews: clone to temp folder first, never review in your main project
- For parallel work: spawn multiple background agents, each in their own workdir
