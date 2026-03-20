---
name: chrome-extension-development
description: >
  Chrome extension development with Manifest V3.
---

# Chrome Extension Development (MV3)

## Manifest V3 Structure
```json
{
 "manifest_version": 3,
 "name": "My Extension",
 "version": "1.0",
 "permissions": ["storage", "activeTab"],
 "action": { "default_popup": "popup.html", "default_icon": "icon.png" },
 "background": { "service_worker": "background.js" },
 "content_scripts": [{ "matches": ["<all_urls>"], "js": ["content.js"] }]
}
```

## Key Components
- **Service Worker** (background.js): Event-driven, no DOM access, handles API calls and state
- **Content Scripts**: Run in page context, access DOM, communicate via messaging
- **Popup**: Small UI when clicking extension icon
- **Options page**: Settings UI

## Messaging
```js
// Content script → Background
chrome.runtime.sendMessage({ type: 'getData', url: location.href }, (response) => { ... });

// Background listener
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
 if (msg.type === 'getData') { fetch(msg.url).then(r => r.json()).then(sendResponse); return true; }
});
```

## Storage
```js
await chrome.storage.local.set({ key: value });
const { key } = await chrome.storage.local.get('key');
// Use storage.sync for cross-device sync (limited to 100KB)
```

## Tips
- Service workers are ephemeral — don't store state in variables, use chrome.storage
- Use `chrome.alarms` instead of `setInterval` (service worker may sleep)
- Test with `chrome://extensions` → Developer mode → Load unpacked
- Use `declarativeNetRequest` instead of deprecated `webRequest` blocking
