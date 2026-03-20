---
name: vector-memory
description: >
  Semantic vector memory using PostgreSQL + pgvector. Use when storing important
  information ("remember this", "save this"), recalling past context ("what do I know
  about", "recall", "what did we decide about"), checking memory stats, or flushing
  daily notes into long-term memory. Also use during heartbeats to flush daily notes.
---

# Vector Memory

Semantic memory system backed by PostgreSQL + pgvector on localhost. Uses Gemini embedding model for 768-dim vectors.

## Prerequisites (NOT YET INSTALLED)

- PostgreSQL 17+ with pgvector extension — **not installed on this machine**
- Python 3 with `psycopg2-binary`
- A free Google Gemini API key (`GEMINI_API_KEY` env var)

## Setup

```bash
# Install PostgreSQL (macOS)
brew install postgresql@17 && brew services start postgresql@17

# Install Python dependency
pip3 install psycopg2-binary

# Create database and table
psql postgres -c "CREATE DATABASE openclaw_memory;"
psql openclaw_memory -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql openclaw_memory -c "CREATE TABLE IF NOT EXISTS memories (
 id SERIAL PRIMARY KEY,
 text TEXT NOT NULL,
 label TEXT,
 category TEXT,
 source TEXT,
 embedding vector(768),
 metadata JSONB DEFAULT '{}',
 created_at TIMESTAMPTZ DEFAULT NOW()
);"
psql openclaw_memory -c "CREATE INDEX IF NOT EXISTS memories_embedding_idx ON memories USING ivfflat (embedding vector_cosine_ops);"

# Set your Gemini API key
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc && source ~/.zshrc
```

## Scripts

All scripts in `scripts/` directory. Require `GEMINI_API_KEY` env var.

### Store a memory
```bash
python3 scripts/memory_store.py "text to remember" --label "short-label" --category "category" --source "conversation"
```
Categories: `youtube`, `leads`, `technical`, `projects`, `personal`, `business`, `daily-note`

### Search memories
```bash
python3 scripts/memory_search.py "natural language query" --limit 5 --min-score 0.3
```
Returns ranked results with similarity scores. Higher = more relevant.

### Flush daily notes into vector DB
```bash
python3 scripts/memory_flush.py # incremental (skips unchanged files)
python3 scripts/memory_flush.py --force # re-flush everything
python3 scripts/memory_flush.py --dry-run # preview only
```
Run during heartbeats to keep vector DB current with daily notes and MEMORY.md.

### Forget / manage memories
```bash
python3 scripts/memory_forget.py --id 123 # delete by id
python3 scripts/memory_forget.py --category "old" # delete by category
python3 scripts/memory_forget.py --older-than 90 # delete older than N days
```

## When to Store
- Key decisions or facts from conversations
- Project milestones, stats, metrics
- Technical setup details (API configs, integrations)
- Anything the user says "remember this" about

## When to Search
- Before answering questions about past work, decisions, or context
- When unsure about something discussed previously
- Supplement flat-file memory search with vector search for better recall

## Heartbeat Integration
Add to your heartbeat routine: run `memory_flush.py` to sync any new/changed daily notes into the vector DB. This keeps semantic search current without manual intervention.

## Database Details
- **DB:** `openclaw_memory` on localhost PostgreSQL 17
- **Table:** `memories` (id, text, label, category, source, embedding, created_at, metadata)
- **Embedding:** Gemini embedding-001, 768 dimensions
- **Index:** IVFFlat with cosine similarity
