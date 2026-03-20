// Audio Recorder Popup Script

let currentMode = 'oneshot';
let currentCategory = 'kick';
let isRecording = false;
let startTime = null;
let timerInterval = null;
let lastFile = null;

// DOM Elements
const modeBtns = document.querySelectorAll('.mode-btn');
const categoryBtns = document.querySelectorAll('#categories .cat-btn');
const loopCategoryBtns = document.querySelectorAll('#loopCategories .cat-btn');
const categoriesDiv = document.getElementById('categories');
const loopCategoriesDiv = document.getElementById('loopCategories');
const filenameInput = document.getElementById('filename');
const recordBtn = document.getElementById('recordBtn');
const statusDiv = document.getElementById('status');
const timerDiv = document.getElementById('timer');
const playBtn = document.getElementById('playBtn');
const openBtn = document.getElementById('openBtn');
const thresholdInput = document.getElementById('threshold');
const thresholdVal = document.getElementById('thresholdVal');
const maxDurationInput = document.getElementById('maxDuration');
const durationVal = document.getElementById('durationVal');
const lastRecordingDiv = document.getElementById('lastRecording');
const lastName = document.getElementById('lastName');
const lastDuration = document.getElementById('lastDuration');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Load saved settings
  chrome.storage.local.get(['mode', 'category', 'threshold', 'maxDuration', 'lastFile'], (result) => {
    if (result.mode) {
      currentMode = result.mode;
      updateModeUI();
    }
    if (result.category) {
      currentCategory = result.category;
      updateCategoryUI();
    }
    if (result.threshold) {
      thresholdInput.value = result.threshold;
      thresholdVal.textContent = result.threshold + 'dB';
    }
    if (result.maxDuration) {
      maxDurationInput.value = result.maxDuration;
      durationVal.textContent = result.maxDuration + 's';
    }
    if (result.lastFile) {
      lastFile = result.lastFile;
      playBtn.disabled = false;
    }
  });
  
  // Mode buttons
  modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      currentMode = btn.dataset.mode;
      updateModeUI();
      updateCategoryVisibility();
      chrome.storage.local.set({ mode: currentMode });
    });
  });
  
  // Category buttons
  categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      currentCategory = btn.dataset.cat;
      updateCategoryUI();
      chrome.storage.local.set({ category: currentCategory });
    });
  });
  
  // Loop category buttons
  loopCategoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      currentCategory = btn.dataset.cat;
      updateCategoryUI();
      chrome.storage.local.set({ category: currentCategory });
    });
  });
  
  // Threshold slider
  thresholdInput.addEventListener('input', () => {
    thresholdVal.textContent = thresholdInput.value + 'dB';
    chrome.storage.local.set({ threshold: parseInt(thresholdInput.value) });
  });
  
  // Duration slider
  maxDurationInput.addEventListener('input', () => {
    durationVal.textContent = maxDurationInput.value + 's';
    chrome.storage.local.set({ maxDuration: parseInt(maxDurationInput.value) });
  });
  
  // Record button
  recordBtn.addEventListener('click', toggleRecording);
  
  // Play button
  playBtn.addEventListener('click', playLast);
  
  // Open folder button
  openBtn.addEventListener('click', openFolder);
  
  // Check if currently recording
  chrome.runtime.sendMessage({ type: 'getStatus' }, (response) => {
    if (response && response.isRecording) {
      startTimerUI(response.startTime);
      recordBtn.classList.remove('idle');
      recordBtn.classList.add('recording');
      recordBtn.textContent = '⏹ STOP';
      isRecording = true;
    }
  });
  
  // Initialize category visibility
  updateModeUI();
  updateCategoryVisibility();
});

function updateModeUI() {
  modeBtns.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === currentMode);
    btn.classList.toggle('loop-mode', btn.dataset.mode === 'loop');
  });
}

function updateCategoryVisibility() {
  if (currentMode === 'loop') {
    categoriesDiv.classList.add('loop-active');
    loopCategoriesDiv.classList.add('loop-active');
  } else {
    categoriesDiv.classList.remove('loop-active');
    loopCategoriesDiv.classList.remove('loop-active');
  }
}

function updateCategoryUI() {
  // Update both sets of buttons
  categoryBtns.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.cat === currentCategory);
  });
  loopCategoryBtns.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.cat === currentCategory);
  });
}

function setStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = 'status ' + type;
}

function startTimerUI(start) {
  startTime = start || Date.now();
  timerDiv.classList.add('recording');
  
  timerInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const seconds = Math.floor(elapsed / 1000);
    const ms = Math.floor((elapsed % 1000) / 10);
    timerDiv.textContent = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
  }, 10);
}

function stopTimerUI() {
  clearInterval(timerInterval);
  timerDiv.classList.remove('recording');
}

async function toggleRecording() {
  if (!isRecording) {
    // Start recording
    isRecording = true;
    startTime = Date.now();
    
    const settings = {
      mode: currentMode,
      category: currentCategory,
      filename: filenameInput.value.trim() || null,
      threshold: parseInt(thresholdInput.value),
      maxDuration: parseInt(maxDurationInput.value)
    };
    
    chrome.runtime.sendMessage({ type: 'startRecording', settings }, (response) => {
      if (response && response.success) {
        setStatus('🔴 Recording... Play your sample!', 'info');
        recordBtn.classList.remove('idle');
        recordBtn.classList.add('recording');
        recordBtn.textContent = '⏹ STOP';
        startTimerUI(startTime);
      } else {
        setStatus('❌ ' + (response?.error || 'Failed to start recording'), 'error');
        isRecording = false;
      }
    });
    
  } else {
    // Stop recording
    stopTimerUI();
    recordBtn.classList.remove('recording');
    recordBtn.classList.add('processing');
    recordBtn.textContent = '⏳ Processing...';
    setStatus('Processing audio...', 'info');
    
    chrome.runtime.sendMessage({ type: 'stopRecording' }, (response) => {
      isRecording = false;
      
      if (response && response.success) {
        const duration = response.duration;
        const filename = response.filename;
        
        setStatus(`✅ Saved: ${filename} (${duration.toFixed(2)}s)`, 'success');
        
        lastFile = response.filepath;
        lastName.textContent = filename;
        lastDuration.textContent = duration.toFixed(2) + 's';
        lastRecordingDiv.style.display = 'block';
        playBtn.disabled = false;
        
        // Save to storage
        chrome.storage.local.set({ lastFile: response.filepath });
        
        // Clear filename input
        filenameInput.value = '';
        
      } else {
        setStatus('❌ ' + (response?.error || 'Recording failed'), 'error');
      }
      
      recordBtn.classList.remove('processing');
      recordBtn.classList.add('idle');
      recordBtn.textContent = '⏺ START RECORDING';
      timerDiv.textContent = '00:00.00';
    });
  }
}

function playLast() {
  chrome.runtime.sendMessage({ type: 'playLast' }, (response) => {
    if (response && response.success) {
      setStatus('▶ Playing last recording...', 'info');
    } else {
      setStatus('❌ ' + (response?.error || 'No recording to play'), 'error');
    }
  });
}

function openFolder() {
  chrome.runtime.sendMessage({ type: 'openFolder' });
}