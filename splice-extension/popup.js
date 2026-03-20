// Splice Audio Downloader - Popup Script

document.addEventListener('DOMContentLoaded', async () => {
  const downloadBtn = document.getElementById('downloadBtn');
  const batchBtn = document.getElementById('batchBtn');
  const statusDiv = document.getElementById('status');
  const sampleInfoDiv = document.getElementById('sampleInfo');
  const sampleNameDiv = document.getElementById('sampleName');
  const sampleIdDiv = document.getElementById('sampleId');
  const formatSelect = document.getElementById('format');
  const prefixInput = document.getElementById('prefix');
  
  let currentTab = null;
  let currentSample = null;
  
  // Show status message
  function showStatus(message, type = 'info') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.classList.remove('hidden');
  }
  
  // Hide status
  function hideStatus() {
    statusDiv.classList.add('hidden');
  }
  
  // Get current tab
  try {
    currentTab = await chrome.tabs.query({ active: true, currentWindow: true }).then(tabs => tabs[0]);
  } catch (e) {
    showStatus('Error getting tab: ' + e.message, 'error');
    return;
  }
  
  if (!currentTab) {
    showStatus('No active tab found', 'error');
    return;
  }
  
  console.log('[Popup] Current tab:', currentTab.url);
  
  // Check if we're on Splice
  if (!currentTab.url || !currentTab.url.includes('splice.com')) {
    showStatus('Please navigate to a Splice sample page', 'error');
    downloadBtn.disabled = true;
    return;
  }
  
  showStatus('Connecting to page...', 'info');
  
  // Request sample info from content script
  function requestSampleInfo() {
    chrome.tabs.sendMessage(currentTab.id, { type: 'GET_SAMPLE_INFO' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('[Popup] Error:', chrome.runtime.lastError);
        showStatus('Error: ' + chrome.runtime.lastError.message, 'error');
        
        // Try to inject content script manually
        console.log('[Popup] Trying to inject content script...');
        chrome.scripting.executeScript({
          target: { tabId: currentTab.id },
          files: ['content.js']
        }).then(() => {
          setTimeout(requestSampleInfo, 500);
        }).catch(err => {
          showStatus('Failed to inject: ' + err.message, 'error');
        });
        return;
      }
      
      console.log('[Popup] Response:', response);
      
      if (response && response.sample) {
        currentSample = response.sample;
        sampleNameDiv.textContent = currentSample.name || 'Unknown';
        sampleIdDiv.textContent = currentSample.id || '-';
        sampleInfoDiv.classList.remove('hidden');
        downloadBtn.disabled = false;
        hideStatus();
      } else {
        showStatus('Play the sample first, then try again', 'info');
      }
    });
  }
  
  // Listen for messages from content script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[Popup] Received message:', message.type);
    
    if (message.type === 'SPLICE_SAMPLE_INFO') {
      currentSample = message.sample;
      sampleNameDiv.textContent = currentSample.name || 'Unknown';
      sampleIdDiv.textContent = currentSample.id || '-';
      sampleInfoDiv.classList.remove('hidden');
      downloadBtn.disabled = false;
      hideStatus();
      sendResponse({ received: true });
    }
    
    if (message.type === 'SPLICE_AUDIO_READY') {
      showStatus(`Audio captured: ${message.name}`, 'success');
    }
    
    if (message.type === 'SPLICE_DOWNLOAD_READY') {
      const prefix = prefixInput.value || 'splice_';
      const filename = `${prefix}${message.name}_${message.sampleId}.wav`;
      
      showStatus('Preparing download...', 'info');
      
      // Send to background for download
      chrome.runtime.sendMessage({
        type: 'DOWNLOAD_WAV',
        name: message.name,
        sampleId: message.sampleId,
        wav: message.wav
      }, (response) => {
        if (response && response.success) {
          showStatus(`Downloaded: ${filename}`, 'success');
        } else {
          showStatus(response?.error || 'Download failed', 'error');
        }
        downloadBtn.disabled = false;
      });
    }
    
    if (message.type === 'SPLICE_DOWNLOAD_ERROR') {
      showStatus(message.error, 'error');
      downloadBtn.disabled = false;
    }
    
    return true; // Keep channel open for async response
  });
  
  // Download button click
  downloadBtn.addEventListener('click', async () => {
    if (!currentTab || !currentSample) return;
    
    downloadBtn.disabled = true;
    showStatus('Requesting audio download...', 'info');
    
    chrome.tabs.sendMessage(currentTab.id, {
      type: 'SPLICE_DOWNLOAD_REQUEST',
      sampleId: currentSample.id
    }, (response) => {
      if (chrome.runtime.lastError) {
        showStatus('Error: ' + chrome.runtime.lastError.message, 'error');
        downloadBtn.disabled = false;
      } else if (response && response.error) {
        showStatus(response.error, 'error');
        downloadBtn.disabled = false;
      }
    });
  });
  
  // Batch button (placeholder)
  batchBtn.addEventListener('click', () => {
    showStatus('Play samples to capture them, then click Download', 'info');
  });
  
  // Initial request
  requestSampleInfo();
});