// Splice Audio Downloader - Background Script (Service Worker)

console.log('[Splice Downloader BG] Service worker started');

// Listen for messages from content script and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Splice Downloader BG] Message:', message.type);
  
  if (message.type === 'DOWNLOAD_WAV') {
    downloadWav(message)
      .then(downloadId => {
        console.log('[Splice Downloader BG] Download started:', downloadId);
        sendResponse({ success: true, downloadId: downloadId });
      })
      .catch(err => {
        console.error('[Splice Downloader BG] Download error:', err);
        sendResponse({ success: false, error: err.message });
      });
    return true; // Keep channel open for async response
  }
});

async function downloadWav(data) {
  const { name, sampleId, wavArray } = data;
  
  // Convert array back to Uint8Array
  const uint8Array = new Uint8Array(wavArray);
  
  // Create base64
  let binary = '';
  const len = uint8Array.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(uint8Array[i]);
  }
  const base64 = btoa(binary);
  
  const filename = `splice_${name}_${sampleId}.wav`;
  const url = 'data:audio/wav;base64,' + base64;
  
  console.log('[Splice Downloader BG] Downloading:', filename, 'size:', uint8Array.length);
  
  return chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
}

// Handle downloads
chrome.downloads.onChanged.addListener((delta) => {
  if (delta.state && delta.state.current === 'complete') {
    console.log('[Splice Downloader BG] Download complete:', delta.id);
  }
});