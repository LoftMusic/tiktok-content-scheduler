# HEARTBEAT.md

## SMART MEMORY LOADING (do this first, every heartbeat)
Before anything else, load context efficiently:
1. Read memory/projects.md - compact project registry (~1K tokens)
2. Read MEMORY.md - curated long-term memory (~3K tokens)
3. Only load daily notes (memory/YYYY-MM-DD.md) when asked about specific past work
4. Only run vector search when a specific question about past work comes up
This gives full context at ~10% of the token cost. Daily notes are archives, not runtime docs.

# Add heartbeat tasks below this line
