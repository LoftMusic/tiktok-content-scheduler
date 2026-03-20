# MEMORY.md — Long-Term Memory

Last updated: 2026-03-20

## Memory System
- **Daily notes**: `memory/YYYY-MM-DD.md` — raw session logs, written automatically, load on-demand
- **MEMORY.md**: this file — curated long-term brain, load every heartbeat (~3K tokens)
- **projects.md**: compact project registry — load every heartbeat (~1K tokens)
- **Vector DB**: PostgreSQL + pgvector, semantic search via AI embeddings — not yet installed
- **Smart loading**: only projects.md + MEMORY.md at startup. Daily notes + vector search = on-demand only.

## About Me
_(Fill in after first conversation — see BOOTSTRAP.md)_

## About My Human
- Name: _(unknown — BOOTSTRAP not completed)_
- Working on: Splice audio sample recording tools (desktop app + browser extension)
- Music production context (uses Volt 1 interface, Splice.com, REAPER)

## Active Work

### splice-desktop (Electron desktop app)
Building a desktop app to capture system audio → trim silence → save categorized WAV samples.
- Uses Python sounddevice (PortAudio) via subprocess for loopback capture
- C4D Python at `C:\Program Files\Maxon Cinema 4D 2024\resource\modules\python\libs\win64\python.exe`
- Python packages: `C:\Users\Studio3\AppData\Roaming\Python\Python311\site-packages`
- Key devices: Device 29 (Stereo Mix/WDM-KS), Device 0 (Microsoft Sound Mapper)
- `asar: false` required — Python can't read from Electron asar archives
- `shell: true` required for spawn — fixes "C:\Program Files not recognized"
- NSIS installer broken (no admin symlink privilege on Windows)
- Current issue: silence trimming / loopback detection being debugged

### splice-recorder (Chrome extension)
Browser extension to record samples directly from Splice.com.
- Manifest V3, content script + background service worker
- FFmpeg WASAPI capture (not DirectShow — can't reach WASAPI loopback)
- Has sophisticated silence trimming: peak-relative threshold, 50ms end shift for oneshots
- Blocked: Splice.com returns 403 — switched to desktop app approach

## Key Technical Decisions
- Volt 1 hardware loopback preferred over virtual cable
- Python sounddevice > FFmpeg for Windows audio (better device enum, callback + blocking support)
- int16 PCM streaming from Python (matches Node.js WAV processing assumption)
- `asar: false` in electron-builder = required for Python subprocess file access
- `shell: true` in Node.js spawn = required for paths with spaces

## Skills Installed
- `skill-guard`: security auditor for skills
- `skill-detector`: pattern detector + skill factory
- `healthcheck`: host security hardening
- `node-connect`: OpenClaw node pairing diagnostics
- `weather`: weather forecasts via wttr.in
- `video-frames`: FFmpeg frame extraction
