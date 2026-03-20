---
name: oracle
description: >
  Best practices for using the oracle CLI (prompt + file bundling, engines, sessions).
---

# oracle — Best Use

Oracle bundles your prompt + selected files into one "one-shot" request so another model can answer with real repo context.

## Recommended Defaults
- Engine: `--engine browser` with GPT-5.2 Pro (`--model gpt-5.2-pro`)
- Expect ~10 min to ~1 hour for complex queries — runs may detach

## Commands
```bash
# Preview (no tokens spent)
oracle --dry-run summary -p "<task>" --file "src/**"

# Token check
oracle --dry-run summary --files-report -p "<task>" --file "src/**"

# Browser run (main path)
oracle --engine browser --model gpt-5.2-pro -p "<task>" --file "src/**"

# Manual paste fallback
oracle --render --copy -p "<task>" --file "src/**"
```

## File Attachment (`--file`)
- Include: `--file "src/**"` or `--file src/index.ts`
- Exclude: `--file "!src/**/*.test.ts"`
- Auto-ignores: node_modules, dist, .git, build, etc.
- Honors .gitignore. Files > 1MB rejected.

## Sessions
- Stored in `~/.oracle/sessions`
- List: `oracle status --hours 72`
- Reattach: `oracle session <id> --render`
- Use `--slug "my-task-name"` for readable IDs

## Prompt Tips
Oracle has ZERO project knowledge. Always include:
- Project briefing (stack, build/test commands, platform)
- Key directories and entrypoints
- Exact question + what you tried + error text
- Constraints and desired output format

## Safety
- Don't attach secrets (.env, key files). Redact aggressively.
