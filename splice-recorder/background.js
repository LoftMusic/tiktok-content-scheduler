// Background script - handles downloads and coordination

let isRecording = false;
let startTime = null;
let lastDownload = null;

// Ensure offscreen document exists
async function ensureOffscreenDocument() {
  const existingContexts = await chrome.runtime.getContexts({
    contextTypes: ['OFFSCREEN_DOCUMENT']
  });
  
  if (existingContexts.length > 0) {
    return true;
  }
  
  try {
    await chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['USER_MEDIA'],
      justification: 'Recording tab audio'
    });
    return true;
  } catch (e) {
    console.error('[Background] Offscreen create error:', e);
    return false;
  }
}

// Listen for extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  console.log('[Background] Icon clicked, tab:', tab.id, 'url:', tab.url);
  
  // Check if this is a Chrome page
  if (tab.url?.startsWith('chrome://') || 
      tab.url?.startsWith('chrome-extension://') ||
      tab.url?.startsWith('about:')) {
    console.log('[Background] Chrome page, cannot inject');
    return;
  }
  
  try {
    // Check if panel already exists
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => !!document.getElementById('audio-recorder-panel')
    });
    
    const panelExists = results?.[0]?.result;
    console.log('[Background] Panel exists:', panelExists);
    
    if (panelExists) {
      // Just show it
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const panel = document.getElementById('audio-recorder-panel');
          if (panel) panel.style.display = 'block';
        }
      });
    } else {
      // Inject content script
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });
      console.log('[Background] Content script injected');
    }
  } catch (e) {
    console.error('[Background] Error:', e);
  }
});

// Message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Background] Message:', message.type);
  
  switch (message.type) {
    case 'getStatus':
      sendResponse({ isRecording, startTime });
      break;
      
    case 'startRecording':
      handleStartRecording(message.settings, sender)
        .then(result => sendResponse(result))
        .catch(err => sendResponse({ success: false, error: String(err) }));
      return true;
      
    case 'stopRecording':
      handleStopRecording(message.settings)
        .then(result => sendResponse(result))
        .catch(err => sendResponse({ success: false, error: String(err) }));
      return true;
      
    case 'saveAudio':
      handleSaveAudio(message.data, message.filename)
        .then(result => sendResponse(result))
        .catch(err => sendResponse({ success: false, error: String(err) }));
      return true;
      
    case 'playLast':
      console.log('[Background] playLast called, lastDownload:', lastDownload);
      
      const doOpen = (downloadId) => {
        chrome.downloads.open(downloadId, () => {
          sendResponse({ success: true });
        });
      };
      
      if (lastDownload) {
        doOpen(lastDownload.id);
      } else {
        // Try to get from storage first (in case background restarted)
        chrome.storage.local.get(['lastDownload'], (result) => {
          if (result.lastDownload) {
            doOpen(result.lastDownload.id);
          } else {
            console.log('[Background] No lastDownload available');
            sendResponse({ success: false, error: 'No recording yet' });
          }
        });
      }
      return true; // Keep channel open for async response
      
    case 'openFolder':
      chrome.downloads.showDefaultFolder();
      sendResponse({ success: true });
      break;
  }
});

async function handleStartRecording(settings, sender) {
  if (isRecording) {
    throw new Error('Already recording');
  }
  
  const tabId = sender.tab?.id;
  
  if (!tabId) {
    throw new Error('Could not determine tab. Please refresh the page and try again.');
  }
  
  try {
    const tab = await chrome.tabs.get(tabId);
    if (tab.url?.startsWith('chrome://') || 
        tab.url?.startsWith('chrome-extension://') ||
        tab.url?.startsWith('about:')) {
      throw new Error('Cannot capture Chrome internal pages. Navigate to a regular website.');
    }
  } catch (e) {
    throw e;
  }
  
  const ok = await ensureOffscreenDocument();
  if (!ok) {
    throw new Error('Could not create offscreen document');
  }
  
  console.log('[Background] Getting stream for tab:', tabId);
  
  try {
    const streamId = await chrome.tabCapture.getMediaStreamId({
      targetTabId: tabId
    });
    
    console.log('[Background] Stream ID:', streamId);
    
    const response = await chrome.runtime.sendMessage({
      type: 'startCapture',
      streamId: streamId,
      settings: settings
    });
    
    if (response.success) {
      isRecording = true;
      startTime = Date.now();
      await chrome.storage.local.set({ isRecording: true, startTime, tabId });
      return { success: true };
    } else {
      throw new Error(response.error || 'Failed to start');
    }
  } catch (e) {
    console.error('[Background] Error:', e);
    throw new Error('Could not capture tab. Make sure you clicked the extension icon first.');
  }
}

async function handleStopRecording(settings) {
  if (!isRecording) {
    return { success: false, error: 'Not recording' };
  }
  
  console.log('[Background] Stopping...');
  
  // IMPORTANT: sendMessage returns a promise - await it before clearing isRecording
  // This prevents a race where the user can click start again while stop is still in flight
  const response = await chrome.runtime.sendMessage({
    type: 'stopCapture',
    settings: settings
  });
  
  isRecording = false;
  startTime = null;
  await chrome.storage.local.set({ isRecording: false });
  
  return response;
}

async function handleSaveAudio(base64Data, filename) {
  console.log('[Background] Saving:', filename);
  
  try {
    const downloadId = await chrome.downloads.download({
      url: base64Data,
      filename: filename,
      saveAs: false
    });
    
    lastDownload = { id: downloadId, filename: filename };
    
    // Persist to storage so it survives background restarts
    chrome.storage.local.set({ lastDownload: lastDownload });
    
    console.log('[Background] Download started:', downloadId);
    
    return { success: true, downloadId: downloadId };
  } catch (err) {
    console.error('[Background] Save error:', err);
    return { success: false, error: String(err) };
  }
}

console.log('[Background] Loaded');