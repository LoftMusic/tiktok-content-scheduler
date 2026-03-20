---
name: here-now
description: >
  Publish files and folders to the web instantly. Use when asked to "publish this",
  "host this", "deploy this", "share this on the web", "make a website", or
  "put this online". Outputs a live URL at <slug>.here.now.
---

# here.now

Publish any file or folder to the web and get a live URL back. Static hosting only.

## Install

```bash
npx skills add heredotnow/skill --skill here-now -g
```

## Requirements

- Required binaries: `curl`, `file`, `jq`
- Optional environment variable: `$HERENOW_API_KEY`

## Publish

```bash
./scripts/publish.sh <file-or-dir>
```

Outputs the live URL (e.g. `https://bright-canvas-a7k2.here.now/`).

Without an API key this creates an **anonymous publish** that expires in 24 hours.
With a saved API key, the publish is permanent.

**File structure:** For HTML sites, place `index.html` at the root of the directory you publish. The directory's contents become the site root.

You can also publish raw files without any HTML. Single files get a rich auto-viewer (images, PDF, video, audio). Multiple files get an auto-generated directory listing.

## Update an existing publish

```bash
./scripts/publish.sh <file-or-dir> --slug <slug>
```

## API key storage

Store your API key securely:

```bash
mkdir -p ~/.herenow && echo "<API_KEY>" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

The script reads from:
1. `--api-key <key>` flag
2. `$HERENOW_API_KEY` environment variable
3. `~/.herenow/credentials` file (recommended)

## Limits

| | Anonymous | Authenticated |
| -------------- | ------------------ | ---------------------------- |
| Max file size | 250 MB | 5 GB |
| Expiry | 24 hours | Permanent (or custom TTL) |
| Rate limit | 5 / hour / IP | 60 / hour / account |
| Account needed | No | Yes (get key at here.now) |

## Getting an API key

1. Sign up at here.now
2. Copy your API key from the dashboard
3. Save it: `mkdir -p ~/.herenow && echo "<API_KEY>" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials`

## Script options

| Flag | Description |
| ---------------------- | -------------------------------------------- |
| `--slug <slug>` | Update existing publish instead of creating |
| `--title <text>` | Viewer title (non-site publishes) |
| `--description <text>` | Viewer description |
| `--ttl <seconds>` | Set expiry (authenticated only) |

Full docs: https://here.now/docs
