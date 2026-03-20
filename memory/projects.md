# projects.md — Active Project Registry

Last updated: 2026-03-20

## Active Projects

| Project | Status | Tech | Key Notes |
|---------|--------|------|-----------|
| splice-desktop | In progress | Electron, Python/sounddevice, FFmpeg | Desktop app capturing system audio via loopback. Uses C4D Python + sounddevice for capture. Current: fixing silence trimming + loopback detection. Exe at dist/win-unpacked/. |
| splice-recorder | In progress | Chrome Extension (Manifest V3), FFmpeg WASAPI | Browser extension to record samples from Splice.com. Has silence trimming with peak-relative threshold. Blocked: Splice returns 403, Splice desktop app used instead. |
| splice-extension | In progress | Chrome Extension | Alternative extension approach. Testing different audio capture methods. |
| SpliceDownloader | In progress | Python | Download manager for Splice audio samples. |

## Splice Desktop Architecture (for reference)
- Python capture: `src/record.py` — sounddevice callback stream → stdout (int16)
- Electron main: `src/main.js` — AudioEngine class, IPC handlers
- Renderer: `src/renderer.html` — Vue-style vanilla JS UI
- Output: `~/Downloads/Audio/splice_samples/{mode}/{category}/`
- Python path: `C:\Program Files\Maxon Cinema 4D 2024\resource\modules\python\libs\win64\python.exe`
- Device 29 = Stereo Mix (Realtek) — WDM-KS, callback-only stream
- Device 0 = Microsoft Sound Mapper — works with blocking reads
- asar: false (required for Python subprocess)
- NSIS installer broken (no admin symlinks)

## Git History
- splice-desktop: v0.8 at commit 2342d1e
- splice-recorder: v1-v3 (tags), chrome extension with trimmed silence
