## [ERR-20260320-001] splice-desktop renderer IPC not firing

**Logged**: 2026-03-20T19:49:00+02:00
**Priority**: critical
**Status**: ✅ FIXED
**Area**: frontend

### Summary
App loads but renderer IPC calls never reach main process. All buttons non-functional.

### Root Causes Found (multiple)
1. **BUG 1**: `minimizeBtn` and `closeBtn` elements null — JS error `Cannot read properties of null (reading 'addEventListener')` at renderer.html line 377. These elements existed when custom titlebar was removed but JS listeners remained. Error crashed entire script before `init()` ran.
2. **BUG 2**: `shell: true` with `spawn(PYTHON_EXE, ['-c', inline_code])` doesn't work for paths with spaces — cmd.exe mangles the inline Python code. Fix: use `exec()` with properly quoted cmd string `"PYTHON_EXE script_path"`.

### Fixes Applied
- Removed dead `minimizeBtn`/`closeBtn` DOM references and event listeners from renderer.html
- Changed get-devices from `spawn(..., { shell: true })` with inline `-c` code to `exec()` with `"PYTHON_EXE script_path"` calling a temp file written via `fs.writeFileSync`
- Applied same fix pattern to all IPC handlers that spawn Python

### Next steps
- Verify audio quality in v0.9 exe
- Consider auto-naming from Splice UI sample text
- Consider adding "Play Last" button

