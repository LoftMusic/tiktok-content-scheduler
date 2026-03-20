## [ERR-20260320-001] splice-desktop renderer IPC not firing

**Logged**: 2026-03-20T19:49:00+02:00
**Priority**: critical
**Status**: investigating
**Area**: frontend

### Summary
App loads but renderer IPC calls never reach main process. All buttons non-functional.

### Symptoms
- App launches, window renders with "Loading devices..." dropdown
- No debug logs for `get-devices: spawning Python...` ever appear in main.log
- Renderer console.log statements (init() called, electronAPI type) never appear
- ALL buttons non-functional (record, open folder, minimize, close, test-python-spawn)
- app.isPackaged: true in logs

### What we've tried
1. Verified main.js has `shell: true` in spawn calls (was missing, now fixed)
2. Added renderer-side undefined check + retry for electronAPI
3. Added debug logging to get-devices handler
4. Killed running instances and rebuilt multiple times
5. Confirmed dist renderer.html IS updated with latest changes (timestamps match)
6. Confirmed dist main.js has debug logging (line 374)
7. Preload script exposes getDevices correctly
8. Python standalone works fine (36 devices detected)

### Possible causes
- Preload script not executing (contextIsolation/blockade)?
- Preload path mismatch in packaged app?
- electronAPI undefined in renderer despite preload running
- Some other JS error in renderer preventing ALL code from running

### Next steps
- Use bug-hunter adversarial review to find root cause
- Check if contextIsolation is preventing preload from working
- Add alert() to renderer to confirm JS is executing at all
- Verify preload.js is being loaded by main.js in packaged app
