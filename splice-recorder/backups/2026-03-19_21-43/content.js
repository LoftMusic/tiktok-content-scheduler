// Content script - injects a floating panel for audio recording
// Only loads when extension icon is clicked

(function() {
  'use strict';
  
  // Avoid double injection
  if (window.__audioRecorderInjected) return;
  window.__audioRecorderInjected = true;
  
  console.log('[Audio Recorder] Content script loaded');
  
  // State
  let isRecording = false;
  let startTime = null;
  let timerInterval = null;
  let currentMode = 'oneshot';
  let currentCategory = 'kick';
  let lastFile = null;
  let detectedSampleName = null;
  let lastPlayedElement = null;
  
  // One Shot categories
  const oneShotCategories = ['kick', 'snare', 'hihat', 'tom', 'clap', 'perc', 'fx', 'vocal', 'other'];
  
  // Loop categories
  const loopCategories = ['fulldrums', 'drumtops', 'kicks', 'snares', 'hihats', 'percussion', 'bass', 'melody', 'fxloop', 'vocals'];
  
  // Tag to category mapping
  const tagToCategory = {
    'kick': 'kick', 'kicks': 'kicks',
    'snare': 'snare', 'snares': 'snares',
    'hihat': 'hihat', 'hihats': 'hihats', 'hi-hat': 'hihats',
    'tom': 'tom', 'toms': 'tom',
    'clap': 'clap', 'claps': 'clap',
    'perc': 'perc', 'percussion': 'percussion', 'percs': 'percussion',
    'drums': 'fulldrums', 'drum': 'fulldrums',
    'drum tops': 'drumtops', 'drumtop': 'drumtops',
    'bass': 'bass', '808': 'bass',
    'melody': 'melody', 'synth': 'melody', 'pad': 'melody', 'lead': 'melody',
    'fx': 'fx', 'fxloop': 'fxloop', 'riser': 'fxloop', 'impact': 'fxloop',
    'vocal': 'vocal', 'vocals': 'vocals', 'vox': 'vocals',
    'loop': 'loop', 'breaks': 'loop'
  };
  
  // Create panel
  function createPanel() {
    // Check if panel already exists
    const existingPanel = document.getElementById('audio-recorder-panel');
    if (existingPanel) {
      // Panel exists, just show it
      existingPanel.style.display = 'block';
      console.log('[Audio Recorder] Panel already exists, showing it');
      return;
    }
    
    console.log('[Audio Recorder] Creating new panel');
    
    const panel = document.createElement('div');
    panel.id = 'audio-recorder-panel';
    panel.innerHTML = `
      <style>
        #audio-recorder-panel {
          position: fixed !important;
          bottom: 20px !important;
          right: 20px !important;
          width: 340px !important;
          min-height: 520px !important;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
          border-radius: 12px !important;
          box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
          z-index: 2147483647 !important;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
          color: white !important;
          font-size: 14px !important;
          overflow: hidden !important;
        }
        #audio-recorder-panel * {
          box-sizing: border-box !important;
        }
        .ar-header {
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          padding: 12px 16px !important;
          background: rgba(0,0,0,0.15) !important;
          border-radius: 12px 12px 0 0 !important;
          cursor: move !important;
          user-select: none !important;
        }
        .ar-title {
          font-weight: 600 !important;
          display: flex !important;
          align-items: center !important;
          gap: 8px !important;
        }
        .ar-close {
          background: rgba(255,255,255,0.2) !important;
          border: none !important;
          color: white !important;
          width: 24px !important;
          height: 24px !important;
          border-radius: 4px !important;
          cursor: pointer !important;
          font-size: 14px !important;
          line-height: 1 !important;
        }
        .ar-close:hover {
          background: rgba(255,255,255,0.3) !important;
        }
        .ar-content {
          padding: 16px !important;
        }
        .ar-section {
          margin-bottom: 12px !important;
        }
        .ar-section-title {
          font-size: 11px !important;
          font-weight: 600 !important;
          text-transform: uppercase !important;
          opacity: 0.7 !important;
          margin-bottom: 6px !important;
        }
        .ar-mode-switch {
          display: flex !important;
          gap: 6px !important;
        }
        .ar-mode-btn {
          flex: 1 !important;
          padding: 8px !important;
          border: 2px solid rgba(255,255,255,0.2) !important;
          border-radius: 6px !important;
          background: transparent !important;
          color: white !important;
          font-size: 10px !important;
          font-weight: 700 !important;
          cursor: pointer !important;
          transition: all 0.2s !important;
        }
        .ar-mode-btn:hover {
          border-color: rgba(255,255,255,0.4) !important;
        }
        .ar-mode-btn.active {
          background: #6b46c1 !important;
          border-color: #6b46c1 !important;
        }
        .ar-mode-btn.loop-mode.active {
          background: #e67e22 !important;
          border-color: #e67e22 !important;
        }
        .ar-categories {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 4px;
        }
        
        #ar-categories {
          display: grid;
        }
        
        #ar-categories.loop-active {
          display: none !important;
        }
        
        #ar-loop-categories {
          display: none;
        }
        
        #ar-loop-categories.loop-active {
          display: grid !important;
        }
        .ar-cat-btn {
          padding: 6px 4px !important;
          border: none !important;
          border-radius: 4px !important;
          background: rgba(255,255,255,0.1) !important;
          color: white !important;
          font-size: 9px !important;
          font-weight: 600 !important;
          cursor: pointer !important;
          transition: all 0.2s !important;
        }
        .ar-cat-btn:hover {
          background: rgba(255,255,255,0.2) !important;
        }
        .ar-cat-btn.active {
          background: #e74c3c !important;
        }
        .ar-filename {
          width: 100% !important;
          padding: 8px 10px !important;
          border: none !important;
          border-radius: 6px !important;
          background: rgba(255,255,255,0.1) !important;
          color: white !important;
          font-size: 13px !important;
        }
        .ar-filename::placeholder {
          color: rgba(255,255,255,0.5) !important;
        }
        .ar-timer {
          font-size: 28px !important;
          font-weight: 700 !important;
          text-align: center !important;
          padding: 12px !important;
          font-family: 'Consolas', monospace !important;
        }
        .ar-timer.recording {
          color: #f39c12 !important;
        }
        .ar-record-btn {
          width: 100% !important;
          padding: 14px !important;
          border: none !important;
          border-radius: 8px !important;
          font-size: 14px !important;
          font-weight: 700 !important;
          cursor: pointer !important;
          transition: all 0.2s !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          gap: 8px !important;
        }
        .ar-record-btn.idle {
          background: #e74c3c !important;
          color: white !important;
        }
        .ar-record-btn.idle:hover {
          background: #c0392b !important;
        }
        .ar-record-btn.recording {
          background: #f39c12 !important;
          color: white !important;
          animation: pulse 1.5s infinite !important;
        }
        .ar-record-btn.processing {
          background: #3498db !important;
          color: white !important;
        }
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(243, 156, 18, 0.4); }
          50% { box-shadow: 0 0 0 10px rgba(243, 156, 18, 0); }
        }
        .ar-status {
          padding: 8px !important;
          border-radius: 6px !important;
          font-size: 12px !important;
          text-align: center !important;
          background: rgba(255,255,255,0.1) !important;
        }
        .ar-status.success { background: rgba(46, 204, 113, 0.3) !important; }
        .ar-status.error { background: rgba(231, 76, 60, 0.3) !important; }
        .ar-status.info { background: rgba(52, 152, 219, 0.3) !important; }
        .ar-actions {
          display: flex !important;
          gap: 8px !important;
        }
        .ar-action-btn {
          flex: 1 !important;
          padding: 8px !important;
          border: none !important;
          border-radius: 6px !important;
          background: rgba(255,255,255,0.1) !important;
          color: white !important;
          font-size: 12px !important;
          cursor: pointer !important;
        }
        .ar-action-btn:hover {
          background: rgba(255,255,255,0.2) !important;
        }
        .ar-action-btn:disabled {
          opacity: 0.5 !important;
          cursor: not-allowed !important;
        }
        .ar-settings {
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          margin-top: 8px !important;
        }
        .ar-settings label {
          font-size: 11px !important;
          flex: 1 !important;
        }
        .ar-settings input[type="range"] {
          flex: 2 !important;
        }
        .ar-settings-value {
          font-size: 11px !important;
          opacity: 0.7 !important;
          min-width: 35px !important;
        }
        .ar-last {
          background: rgba(0,0,0,0.2) !important;
          border-radius: 6px !important;
          padding: 8px !important;
          font-size: 11px !important;
        }
      </style>
      
      <div class="ar-header" id="ar-header">
        <div class="ar-title">🎵 Audio Recorder</div>
        <button class="ar-close" id="ar-close">✕</button>
      </div>
      
      <div class="ar-content" id="ar-content">
        <div class="ar-section">
          <div class="ar-section-title">Mode</div>
          <div class="ar-mode-switch" id="ar-mode-switch">
            <button class="ar-mode-btn active" data-mode="oneshot">ONE SHOT</button>
            <button class="ar-mode-btn" data-mode="loop">LOOP</button>
          </div>
        </div>
        
        <div class="ar-section" id="ar-category-section">
          <div class="ar-section-title">Category</div>
          <div class="ar-categories" id="ar-categories"></div>
          <div class="ar-categories" id="ar-loop-categories" style="display: none;"></div>
        </div>
        
        <div class="ar-section">
          <div class="ar-section-title">Filename (optional)</div>
          <input type="text" class="ar-filename" id="ar-filename" placeholder="Auto-generated if empty...">
        </div>
        
        <div class="ar-timer" id="ar-timer">00:00.00</div>
        
        <button class="ar-record-btn idle" id="ar-record-btn">⏺ START RECORDING</button>
        
        <div class="ar-status info" id="ar-status">Ready - Click to start recording</div>
        
        <div class="ar-actions">
          <button class="ar-action-btn" id="ar-play-btn" disabled>▶ Play Last</button>
          <button class="ar-action-btn" id="ar-folder-btn">📁 Open Folder</button>
        </div>
        
        <div class="ar-settings">
          <label>Threshold</label>
          <input type="range" id="ar-threshold" min="-60" max="-20" value="-40">
          <span class="ar-settings-value" id="ar-threshold-val">-40dB</span>
        </div>
        <div class="ar-settings">
          <label>Fade-out</label>
          <input type="range" id="ar-fadeout" min="0" max="200" value="50">
          <span class="ar-settings-value" id="ar-fadeout-val">50ms</span>
        </div>
        
        <div class="ar-last" id="ar-last" style="display: none;">
          <strong>Last:</strong> <span id="ar-last-name">-</span>
        </div>
      </div>
    `;
    
    document.body.appendChild(panel);
    
    // Populate one-shot categories
    const catContainer = panel.querySelector('#ar-categories');
    oneShotCategories.forEach(cat => {
      const btn = document.createElement('button');
      btn.className = 'ar-cat-btn' + (cat === currentCategory ? ' active' : '');
      btn.textContent = cat.toUpperCase();
      btn.dataset.cat = cat;
      btn.addEventListener('click', () => selectCategory(cat));
      catContainer.appendChild(btn);
    });
    
    // Populate loop categories
    const loopCatContainer = panel.querySelector('#ar-loop-categories');
    loopCategories.forEach(cat => {
      const btn = document.createElement('button');
      btn.className = 'ar-cat-btn';
      btn.textContent = cat.toUpperCase();
      btn.dataset.cat = cat;
      btn.addEventListener('click', () => selectCategory(cat));
      loopCatContainer.appendChild(btn);
    });
    
    // Event listeners
    setupEventListeners(panel);
    
    // Make draggable
    makeDraggable(panel, panel.querySelector('#ar-header'));
    
    console.log('[Audio Recorder] Panel created');
  }
  
  function selectCategory(cat) {
    currentCategory = cat;
    document.querySelectorAll('#audio-recorder-panel .ar-cat-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.cat === cat);
    });
  }
  
  function selectMode(mode) {
    currentMode = mode;
    document.querySelectorAll('#audio-recorder-panel .ar-mode-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === mode);
      btn.classList.toggle('loop-mode', btn.dataset.mode === 'loop');
    });
    
    // Show/hide appropriate category sets
    const catContainer = panel.querySelector('#ar-categories');
    const loopCatContainer = panel.querySelector('#ar-loop-categories');
    if (mode === 'loop') {
      catContainer.classList.add('loop-active');
      loopCatContainer.classList.add('loop-active');
    } else {
      catContainer.classList.remove('loop-active');
      loopCatContainer.classList.remove('loop-active');
    }
  }
  
  function setupEventListeners(panel) {
    // Close button
    panel.querySelector('#ar-close').addEventListener('click', () => {
      panel.style.display = 'none';
    });
    
    // Mode buttons
    panel.querySelectorAll('.ar-mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        selectMode(btn.dataset.mode);
      });
    });
    
    // Threshold
    const thresholdInput = panel.querySelector('#ar-threshold');
    const thresholdVal = panel.querySelector('#ar-threshold-val');
    thresholdInput.addEventListener('input', () => {
      thresholdVal.textContent = thresholdInput.value + 'dB';
    });
    
    // Fadeout
    const fadeoutInput = panel.querySelector('#ar-fadeout');
    const fadeoutVal = panel.querySelector('#ar-fadeout-val');
    fadeoutInput.addEventListener('input', () => {
      fadeoutVal.textContent = fadeoutInput.value + 'ms';
    });
    
    // Record button
    const recordBtn = panel.querySelector('#ar-record-btn');
    recordBtn.addEventListener('click', toggleRecording);
    
    // Play last
    panel.querySelector('#ar-play-btn').addEventListener('click', playLast);
    
    // Open folder
    panel.querySelector('#ar-folder-btn').addEventListener('click', openFolder);
    
    // Check status on load
    chrome.runtime.sendMessage({ type: 'getStatus' }, (response) => {
      if (response && response.isRecording) {
        isRecording = true;
        startTime = response.startTime;
        updateUI();
        startTimer();
      }
    });
  }
  
  function makeDraggable(panel, header) {
    let isDragging = false;
    let offsetX = 0, offsetY = 0;
    
    header.addEventListener('mousedown', (e) => {
      if (e.target.closest('button')) return;
      isDragging = true;
      const rect = panel.getBoundingClientRect();
      offsetX = e.clientX - rect.left;
      offsetY = e.clientY - rect.top;
      panel.style.left = rect.left + 'px';
      panel.style.top = rect.top + 'px';
      panel.style.right = 'auto';
      panel.style.bottom = 'auto';
      e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      let newX = e.clientX - offsetX;
      let newY = e.clientY - offsetY;
      
      // Keep within viewport
      const maxX = window.innerWidth - panel.offsetWidth;
      const maxY = window.innerHeight - panel.offsetHeight;
      newX = Math.max(0, Math.min(newX, maxX));
      newY = Math.max(0, Math.min(newY, maxY));
      
      panel.style.left = newX + 'px';
      panel.style.top = newY + 'px';
    });
    
    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }
  
  function setStatus(message, type = 'info') {
    const status = document.querySelector('#ar-status');
    if (status) {
      status.textContent = message;
      status.className = 'ar-status ' + type;
    }
  }
  
  function updateUI() {
    const recordBtn = document.querySelector('#ar-record-btn');
    const timer = document.querySelector('#ar-timer');
    
    if (!recordBtn) return;
    
    if (isRecording) {
      recordBtn.className = 'ar-record-btn recording';
      recordBtn.textContent = '⏹ STOP';
      if (timer) timer.classList.add('recording');
    } else {
      recordBtn.className = 'ar-record-btn idle';
      recordBtn.textContent = '⏺ START RECORDING';
      if (timer) timer.classList.remove('recording');
    }
  }
  
  function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
      if (!isRecording || !startTime) return;
      
      const elapsed = Date.now() - startTime;
      const seconds = Math.floor(elapsed / 1000);
      const ms = Math.floor((elapsed % 1000) / 10);
      const timer = document.querySelector('#ar-timer');
      if (timer) {
        timer.textContent = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
      }
    }, 50);
  }
  
  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }
  
  async function toggleRecording() {
    // Check if we can capture this page
    if (window.location.protocol === 'chrome:' || 
        window.location.protocol === 'chrome-extension:' ||
        window.location.protocol === 'about:') {
      setStatus('❌ Cannot capture Chrome pages', 'error');
      return;
    }
    
    if (!isRecording) {
      // Get filename: from input OR detected name OR fallback
      const inputName = document.querySelector('#ar-filename')?.value?.trim();
      const filename = inputName || detectedSampleName || null;
      
      console.log('[Audio Recorder] Starting recording, filename:', filename, 'detected:', detectedSampleName);
      
      const settings = {
        mode: currentMode,
        category: currentCategory,
        filename: filename,
        threshold: parseInt(document.querySelector('#ar-threshold')?.value || '-40'),
        fadeout: parseInt(document.querySelector('#ar-fadeout')?.value || '50'),
        maxDuration: currentMode === 'loop' ? 60 : 30
      };
      
      setStatus('Starting...', 'info');
      
      chrome.runtime.sendMessage({ type: 'startRecording', settings }, (response) => {
        if (response && response.success) {
          isRecording = true;
          startTime = Date.now();
          updateUI();
          startTimer();
          setStatus('🔴 Recording... Play your sample!', 'info');
          // Don't clear filename - keep it for reference
        } else {
          setStatus('❌ ' + (response?.error || 'Failed to start'), 'error');
        }
      });
    } else {
      // Stop recording
      stopTimer();
      
      // Get filename at stop time too (in case user typed after starting)
      const inputName = document.querySelector('#ar-filename')?.value?.trim();
      const filename = inputName || detectedSampleName || null;
      
      const settings = {
        mode: currentMode,
        category: currentCategory,
        filename: filename,
        threshold: parseInt(document.querySelector('#ar-threshold')?.value || '-40'),
        fadeout: parseInt(document.querySelector('#ar-fadeout')?.value || '50')
      };
      
      const recordBtn = document.querySelector('#ar-record-btn');
      if (recordBtn) {
        recordBtn.className = 'ar-record-btn processing';
        recordBtn.textContent = '⏳ Processing...';
      }
      setStatus('Processing audio...', 'info');
      
      chrome.runtime.sendMessage({ type: 'stopRecording', settings }, (response) => {
        isRecording = false;
        updateUI();
        
        if (response && response.success) {
          setStatus(`✅ Saved: ${response.filename} (${response.duration.toFixed(2)}s)`, 'success');
          lastFile = response;
          const playBtn = document.querySelector('#ar-play-btn');
          if (playBtn) playBtn.disabled = false;
          const lastDiv = document.querySelector('#ar-last');
          const lastName = document.querySelector('#ar-last-name');
          if (lastDiv) lastDiv.style.display = 'block';
          if (lastName) lastName.textContent = response.filename;
        } else {
          setStatus('❌ ' + (response?.error || 'Recording failed'), 'error');
        }
        
        const timer = document.querySelector('#ar-timer');
        if (timer) timer.textContent = '00:00.00';
      });
    }
  }
  
  function playLast() {
    chrome.runtime.sendMessage({ type: 'playLast' });
  }
  
  function openFolder() {
    chrome.runtime.sendMessage({ type: 'openFolder' });
  }
  
  // Listen for messages from background
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'showPanel') {
      createPanel();
      sendResponse({ success: true });
    }
  });
  
  // Auto-show panel when script loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createPanel);
  } else {
    setTimeout(createPanel, 100);
  }
  
  // ========== SAMPLE DETECTION ==========
  
  function detectSampleInfo() {
    // Find the currently focused/playing sample row - more selectors for Splice
    // Includes: main catalog (asset-list-row), similar sounds (sp-asset-row), focused/hover states
    const row = document.querySelector(
      '.asset-list-row.list-focused, ' +
      '[role="row"].asset-list-row:focus, ' +
      '[role="row"]:focus-within, ' +
      'core-sample-asset-list-row.list-focused, ' +
      '.asset-list-row:focus-within, ' +
      'sp-asset-row.focused, ' +
      'sp-asset-row.list-focused, ' +
      'sp-asset-row:hover, ' +
      'sp-asset-row:focus-within'
    );
    
    if (!row) {
      // Fallback: find any row with play button that was recently interacted
      const allRows = document.querySelectorAll('[role="row"].asset-list-row, sp-asset-row');
      for (const r of allRows) {
        if (r.matches(':hover, :focus-within') || r.classList.contains('list-focused') || r.classList.contains('focused')) {
          return extractSampleInfo(r);
        }
      }
      return null;
    }
    
    return extractSampleInfo(row);
  }
  
  function extractSampleInfo(row) {
    // Get filename - multiple selectors for both main catalog and similar sounds
    // Main catalog: .filename h6, similar sounds: div.filename[data-qa="asset-filename"]
    const filenameEl = row.querySelector(
      '.filename, h6.filename, [type="filename"] h6, ' +
      '.asset-list-row-cell-filename-tags h6, ' +
      'div.filename[data-qa="asset-filename"], ' +
      '.cell--filename .filename'
    );
    let filename = filenameEl?.textContent?.trim()?.replace(/\.wav$/i, '') || null;
    
    // Clean up filename - remove any leading/trailing junk
    if (filename) {
      filename = filename.replace(/^[\s\n\r]+|[\s\n\r]+$/g, '');
    }
    
    // Get tags - multiple selectors for both views
    const tagEls = row.querySelectorAll(
      'sp-tag, .tag, a.tag, [sp-tag], ' +
      'sp-tags a.tag, ' +
      '.cell--filename sp-tags .tag'
    );
    const tags = [];
    tagEls.forEach(tag => {
      const text = tag.textContent?.trim().toLowerCase();
      if (text && text.length > 0 && text.length < 30 && !tags.includes(text)) {
        tags.push(text);
      }
    });
    
    if (filename || tags.length > 0) {
      console.log('[Audio Recorder] Detected:', filename, 'tags:', tags);
      return { filename, tags };
    }
    
    return null;
  }
  
  function getCategoryFromTags(tags) {
    // Check tags for category match
    for (const tag of tags) {
      if (tagToCategory[tag]) {
        return tagToCategory[tag];
      }
    }
    return null;
  }
  
  // Watch for play button clicks to detect sample
  document.addEventListener('click', (e) => {
    const playBtn = e.target.closest('[aria-label="play"], [data-qa="playPlaybackButton"]');
    if (playBtn) {
      console.log('[Audio Recorder] Play button clicked');
      setTimeout(() => {
        const info = detectSampleInfo();
        if (info?.filename) {
          detectedSampleName = info.filename;
          
          // Auto-fill filename input
          const filenameInput = document.querySelector('#ar-filename');
          if (filenameInput) {
            filenameInput.value = detectedSampleName;
          }
          
          // Try to detect category from tags
          const cat = getCategoryFromTags(info.tags);
          if (cat) {
            currentCategory = cat;
            selectCategory(cat);
            
            // Auto-switch mode based on category
            if (['fulldrums', 'drumtops', 'kicks', 'snares', 'hihats', 'percussion', 'bass', 'melody', 'fxloop', 'vocals'].includes(cat)) {
              selectMode('loop');
            } else {
              selectMode('oneshot');
            }
          }
          
          setStatus(`🎵 Detected: ${detectedSampleName}`, 'info');
        }
      }, 300);
    }
  }, true);
  
  // Also watch for DOM changes to update detection
  const observer = new MutationObserver((mutations) => {
    const focusedRow = document.querySelector('.asset-list-row.list-focused, [role="row"].asset-list-row:focus');
    if (focusedRow && focusedRow !== lastPlayedElement) {
      lastPlayedElement = focusedRow;
      const info = detectSampleInfo();
      if (info?.filename) {
        detectedSampleName = info.filename;
        console.log('[Audio Recorder] Row changed:', detectedSampleName);
      }
    }
  });
  
  if (document.body) {
    observer.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      observer.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
    });
  }
  
})();