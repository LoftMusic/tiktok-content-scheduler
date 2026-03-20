// Splice Audio Downloader - Content Script
// Intercept audio at multiple points

(function() {
  'use strict';
  
  console.log('[Splice Downloader] Content script loading...');
  
  if (window.__spliceDownloaderInjected) return;
  window.__spliceDownloaderInjected = true;
  
  const audioBuffers = new Map();
  let currentSample = { id: null, name: null };
  let panel = null;
  
  // ========== INTERCEPT AUDIO CONTEXT ==========
  
  // Hook AudioContext creation
  const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
  
  window.AudioContext = function(...args) {
    console.log('[Splice Downloader] AudioContext created');
    const ctx = new OriginalAudioContext(...args);
    hookAudioContext(ctx);
    return ctx;
  };
  
  window.webkitAudioContext = window.AudioContext;
  
  function hookAudioContext(ctx) {
    // Hook createBuffer
    const origCreateBuffer = ctx.createBuffer.bind(ctx);
    ctx.createBuffer = function(...args) {
      const buffer = origCreateBuffer(...args);
      console.log('[Splice Downloader] createBuffer called');
      return buffer;
    };
    
    // Hook createBufferSource
    const origCreateBufferSource = ctx.createBufferSource.bind(ctx);
    ctx.createBufferSource = function() {
      const source = origCreateBufferSource();
      hookBufferSource(source);
      return source;
    };
    
    // Hook decodeAudioData
    const origDecodeAudioData = ctx.decodeAudioData.bind(ctx);
    ctx.decodeAudioData = function(arrayBuffer, success, error) {
      console.log('[Splice Downloader] decodeAudioData called, size:', arrayBuffer?.byteLength);
      
      const bufferClone = arrayBuffer.slice(0);
      
      return origDecodeAudioData(
        bufferClone,
        (audioBuffer) => {
          console.log('[Splice Downloader] ✓ Audio decoded:', audioBuffer.duration + 's');
          captureAudioBuffer(audioBuffer);
          if (success) success(audioBuffer);
        },
        error
      );
    };
  }
  
  // Hook AudioBufferSourceNode.buffer setter
  function hookBufferSource(source) {
    let _buffer = null;
    
    Object.defineProperty(source, 'buffer', {
      get() { return _buffer; },
      set(newBuffer) {
        console.log('[Splice Downloader] Buffer set on source:', newBuffer?.duration + 's');
        if (newBuffer && newBuffer.duration > 0) {
          captureAudioBuffer(newBuffer);
        }
        _buffer = newBuffer;
      },
      configurable: true
    });
  }
  
  // Hook existing AudioContext if present
  if (window.AudioContext.prototype.decodeAudioData) {
    const origProtoDecode = window.AudioContext.prototype.decodeAudioData;
    window.AudioContext.prototype.decodeAudioData = function(arrayBuffer, success, error) {
      console.log('[Splice Downloader] proto decodeAudioData, size:', arrayBuffer?.byteLength);
      
      return origProtoDecode.call(
        this,
        arrayBuffer,
        (audioBuffer) => {
          captureAudioBuffer(audioBuffer);
          if (success) success(audioBuffer);
        },
        error
      );
    };
  }
  
  // ========== INTERCEPT FETCH ==========
  
  const origFetch = window.fetch;
  window.fetch = async function(url, options) {
    const urlStr = typeof url === 'string' ? url : url?.url || '';
    const response = await origFetch.call(this, url, options);
    
    const contentType = response.headers.get('content-type') || '';
    const isAudio = contentType.includes('audio') || 
                    urlStr.includes('.mp3') || 
                    urlStr.includes('.wav') ||
                    urlStr.includes('s3.amazonaws.com') ||
                    urlStr.includes('spliceproduction') ||
                    urlStr.includes('audio_sample');
    
    if (isAudio) {
      console.log('[Splice Downloader] Audio fetch:', urlStr.substring(0, 100), contentType);
      
      try {
        const clone = response.clone();
        const buffer = await clone.arrayBuffer();
        
        console.log('[Splice Downloader] Buffer size:', buffer.byteLength);
        
        // Try to decode
        try {
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const audioBuffer = await ctx.decodeAudioData(buffer);
          captureAudioBuffer(audioBuffer);
          ctx.close();
        } catch (e) {
          console.log('[Splice Downloader] Could not decode fetch audio:', e.message);
          // Still save the raw buffer
          if (buffer.byteLength > 1000) {
            const id = currentSample.id || 'raw_' + Date.now();
            audioBuffers.set(id, {
              type: 'raw',
              buffer: buffer,
              name: currentSample.name || 'sample'
            });
            updateUI();
            showStatus(`✓ Captured raw audio (${Math.round(buffer.byteLength/1024)}KB)`, 'success');
          }
        }
      } catch (e) {
        console.log('[Splice Downloader] Fetch intercept error:', e.message);
      }
    }
    
    return response;
  };
  
  // ========== INTERCEPT XHR ==========
  
  const OrigXHR = window.XMLHttpRequest;
  window.XMLHttpRequest = function() {
    const xhr = new OrigXHR();
    let _url = '';
    
    const origOpen = xhr.open;
    xhr.open = function(method, url) {
      _url = url;
      return origOpen.apply(this, arguments);
    };
    
    const origSend = xhr.send;
    xhr.send = function() {
      if (_url.includes('.mp3') || _url.includes('audio') || _url.includes('s3.amazonaws.com')) {
        console.log('[Splice Downloader] XHR:', _url.substring(0, 80));
        
        xhr.addEventListener('load', function() {
          if (xhr.response instanceof ArrayBuffer && xhr.response.byteLength > 0) {
            console.log('[Splice Downloader] XHR response:', xhr.response.byteLength, 'bytes');
            processArrayBuffer(xhr.response);
          }
        });
      }
      
      return origSend.apply(this, arguments);
    };
    
    return xhr;
  };
  
  // ========== WATCH AUDIO ELEMENTS ==========
  
  function watchForAudioElements() {
    const processElement = (el) => {
      if (el.__spliced) return;
      el.__spliced = true;
      
      console.log('[Splice Downloader] Found audio/video element:', el.src?.substring(0, 50));
      
      // Watch for play
      el.addEventListener('play', () => {
        console.log('[Splice Downloader] Audio element playing');
        tryCaptureFromElement(el);
      }, { once: true });
      
      // Watch for canplaythrough
      el.addEventListener('canplaythrough', () => {
        console.log('[Splice Downloader] Audio can play through');
      }, { once: true });
    };
    
    // Existing elements
    document.querySelectorAll('audio, video').forEach(processElement);
    
    // Watch for new elements
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.tagName === 'AUDIO' || node.tagName === 'VIDEO') {
            processElement(node);
          }
          if (node.querySelectorAll) {
            node.querySelectorAll('audio, video').forEach(processElement);
          }
        });
      });
    });
    
    observer.observe(document.body, { subtree: true, childList: true });
  }
  
  async function tryCaptureFromElement(element) {
    try {
      // Method 1: CaptureStream + MediaRecorder
      if (element.captureStream || element.mozCaptureStream) {
        console.log('[Splice Downloader] Trying MediaRecorder...');
        
        const stream = element.captureStream ? element.captureStream() : element.mozCaptureStream();
        const tracks = stream.getAudioTracks();
        
        if (tracks.length > 0) {
          const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
          const chunks = [];
          
          recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
          };
          
          recorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            const id = currentSample.id || 'rec_' + Date.now();
            
            audioBuffers.set(id, {
              type: 'webm',
              blob: blob,
              name: currentSample.name || 'sample'
            });
            
            console.log('[Splice Downloader] ✓ MediaRecorder captured:', blob.size, 'bytes');
            updateUI();
            showStatus(`✓ Captured: ${currentSample.name || 'sample'}`, 'success');
          };
          
          recorder.start();
          
          const duration = Math.min((element.duration || 10), 30);
          setTimeout(() => {
            if (recorder.state === 'recording') {
              recorder.stop();
            }
          }, duration * 1000 + 500);
        }
      }
      
      // Method 2: Fetch the src directly
      if (element.src && !element.src.startsWith('blob:')) {
        console.log('[Splice Downloader] Fetching audio src...');
        try {
          const response = await fetch(element.src);
          const buffer = await response.arrayBuffer();
          await processArrayBuffer(buffer);
        } catch (e) {
          console.log('[Splice Downloader] Could not fetch src:', e.message);
        }
      }
      
    } catch (e) {
      console.log('[Splice Downloader] Capture from element error:', e.message);
    }
  }
  
  // ========== PROCESS AUDIO BUFFER ==========
  
  async function processArrayBuffer(buffer) {
    if (!buffer || buffer.byteLength < 100) return;
    
    console.log('[Splice Downloader] Processing buffer:', buffer.byteLength, 'bytes');
    
    // Try to decode
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await ctx.decodeAudioData(buffer.slice(0));
      captureAudioBuffer(audioBuffer);
      ctx.close();
    } catch (e) {
      console.log('[Splice Downloader] Could not decode, saving raw:', e.message);
      
      // Save as raw buffer
      const id = currentSample.id || 'raw_' + Date.now();
      audioBuffers.set(id, {
        type: 'raw',
        buffer: buffer,
        name: currentSample.name || 'sample'
      });
      updateUI();
      showStatus(`✓ Captured raw: ${Math.round(buffer.byteLength/1024)}KB`, 'success');
    }
  }
  
  function captureAudioBuffer(audioBuffer) {
    if (!audioBuffer || audioBuffer.duration < 0.01) {
      console.log('[Splice Downloader] Invalid buffer');
      return;
    }
    
    const id = currentSample.id || 'buffer_' + Date.now();
    
    // Don't overwrite if we have this
    if (audioBuffers.has(id)) {
      console.log('[Splice Downloader] Already have buffer for:', id);
      return;
    }
    
    audioBuffers.set(id, {
      type: 'wav',
      buffer: audioBuffer,
      name: currentSample.name || 'sample',
      duration: audioBuffer.duration,
      sampleRate: audioBuffer.sampleRate
    });
    
    console.log('[Splice Downloader] ✓ CAPTURED:', currentSample.name, '-', audioBuffer.duration.toFixed(2) + 's');
    updateUI();
    showStatus(`✓ Captured: ${currentSample.name || 'sample'}`, 'success');
  }
  
  // ========== UI ==========
  
  function createPanel() {
    if (document.getElementById('splice-downloader-panel')) return;
    
    panel = document.createElement('div');
    panel.id = 'splice-downloader-panel';
    panel.innerHTML = `
      <style>
        #splice-downloader-panel {
          position: fixed !important;
          bottom: 20px !important;
          right: 20px !important;
          width: 300px !important;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
          border-radius: 12px !important;
          box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
          z-index: 2147483647 !important;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
          color: white !important;
          font-size: 14px !important;
        }
        #splice-downloader-panel * { box-sizing: border-box !important; }
        .sdl-header {
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          padding: 12px 16px !important;
          background: rgba(0,0,0,0.15) !important;
          border-radius: 12px 12px 0 0 !important;
          cursor: move !important;
        }
        .sdl-title { font-weight: 600 !important; }
        .sdl-minimize {
          background: rgba(255,255,255,0.2) !important;
          border: none !important;
          color: white !important;
          width: 24px !important;
          height: 24px !important;
          border-radius: 4px !important;
          cursor: pointer !important;
        }
        .sdl-content { padding: 16px !important; }
        .sdl-content.hidden { display: none !important; }
        .sdl-info {
          background: rgba(255,255,255,0.1) !important;
          border-radius: 8px !important;
          padding: 12px !important;
          margin-bottom: 12px !important;
        }
        .sdl-name { font-weight: 600 !important; margin-bottom: 4px !important; word-break: break-word !important; }
        .sdl-id { font-size: 10px !important; opacity: 0.7 !important; font-family: monospace !important; }
        .sdl-status {
          padding: 8px 12px !important;
          border-radius: 6px !important;
          font-size: 12px !important;
          margin-bottom: 12px !important;
          background: rgba(255,255,255,0.1) !important;
        }
        .sdl-status.success { background: rgba(72, 187, 120, 0.4) !important; }
        .sdl-status.error { background: rgba(245, 101, 101, 0.4) !important; }
        .sdl-status.waiting { background: rgba(236, 201, 75, 0.4) !important; }
        .sdl-btn {
          width: 100% !important;
          padding: 10px 16px !important;
          border: none !important;
          border-radius: 6px !important;
          font-size: 13px !important;
          font-weight: 600 !important;
          cursor: pointer !important;
          margin-bottom: 8px !important;
        }
        .sdl-btn:disabled { opacity: 0.5 !important; cursor: not-allowed !important; }
        .sdl-btn-primary { background: white !important; color: #6b46c1 !important; }
        .sdl-btn-secondary { background: rgba(255,255,255,0.2) !important; color: white !important; }
        .sdl-count { text-align: center !important; font-size: 11px !important; opacity: 0.8 !important; margin-top: 8px !important; }
      </style>
      
      <div class="sdl-header" id="sdl-header">
        <div class="sdl-title">🎵 Splice Downloader</div>
        <button class="sdl-minimize" id="sdl-minimize">−</button>
      </div>
      
      <div class="sdl-content" id="sdl-content">
        <div class="sdl-info" id="sdl-info" style="display:none;">
          <div class="sdl-name" id="sdl-name">-</div>
          <div class="sdl-id" id="sdl-id">-</div>
        </div>
        
        <div class="sdl-status waiting" id="sdl-status">▶️ Play a sample to capture</div>
        
        <button class="sdl-btn sdl-btn-primary" id="sdl-download" disabled>📥 Download Sample</button>
        <button class="sdl-btn sdl-btn-secondary" id="sdl-download-all">📦 Download All (<span id="sdl-count">0</span>)</button>
        
        <div class="sdl-count">Captures appear after playing</div>
      </div>
    `;
    
    document.body.appendChild(panel);
    
    // Minimize
    panel.querySelector('#sdl-minimize').addEventListener('click', () => {
      const content = panel.querySelector('#sdl-content');
      const btn = panel.querySelector('#sdl-minimize');
      content.classList.toggle('hidden');
      btn.textContent = content.classList.contains('hidden') ? '+' : '−';
    });
    
    // Draggable
    const header = panel.querySelector('#sdl-header');
    let dragging = false, offsetX = 0, offsetY = 0;
    
    header.addEventListener('mousedown', (e) => {
      dragging = true;
      offsetX = e.clientX - panel.offsetLeft;
      offsetY = e.clientY - panel.offsetTop;
      panel.style.right = 'auto';
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!dragging) return;
      panel.style.left = (e.clientX - offsetX) + 'px';
      panel.style.top = (e.clientY - offsetY) + 'px';
    });
    
    document.addEventListener('mouseup', () => dragging = false);
    
    // Buttons
    panel.querySelector('#sdl-download').addEventListener('click', () => {
      const id = currentSample.id && audioBuffers.has(currentSample.id) 
        ? currentSample.id 
        : audioBuffers.keys().next().value;
      
      if (id) {
        downloadSample(id);
      } else {
        showStatus('❌ No audio captured!', 'error');
      }
    });
    
    panel.querySelector('#sdl-download-all').addEventListener('click', () => {
      if (audioBuffers.size === 0) {
        showStatus('❌ No samples!', 'error');
        return;
      }
      let i = 0;
      audioBuffers.forEach((_, id) => {
        setTimeout(() => downloadSample(id), i++ * 300);
      });
    });
    
    console.log('[Splice Downloader] Panel created');
  }
  
  function updateUI() {
    if (!panel) return;
    
    const info = panel.querySelector('#sdl-info');
    const name = panel.querySelector('#sdl-name');
    const id = panel.querySelector('#sdl-id');
    const downloadBtn = panel.querySelector('#sdl-download');
    const count = panel.querySelector('#sdl-count');
    
    if (currentSample.id) {
      info.style.display = 'block';
      name.textContent = currentSample.name || 'Unknown';
      id.textContent = currentSample.id;
      downloadBtn.disabled = !audioBuffers.has(currentSample.id) && audioBuffers.size === 0;
    }
    
    count.textContent = audioBuffers.size;
    
    // Enable download if we have anything
    if (audioBuffers.size > 0) {
      downloadBtn.disabled = false;
    }
  }
  
  function showStatus(msg, type = '') {
    if (!panel) return;
    const status = panel.querySelector('#sdl-status');
    status.textContent = msg;
    status.className = 'sdl-status ' + type;
  }
  
  // ========== HELPERS ==========
  
  function getSampleId() {
    const match = window.location.pathname.match(/\/sounds\/sample\/([a-f0-9]+)/);
    return match ? match[1] : null;
  }
  
  function getSampleName() {
    const selectors = ['h1', '[data-testid="sample-name"]', '.sample-name', '.sound-title'];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el?.textContent?.trim()) return el.textContent.trim().substring(0, 100);
    }
    return 'unknown';
  }
  
  function updateSampleInfo() {
    currentSample.id = getSampleId();
    currentSample.name = getSampleName();
    console.log('[Splice Downloader] Sample:', currentSample);
    updateUI();
  }
  
  function audioBufferToWav(buffer) {
    const numCh = buffer.numberOfChannels;
    const sr = buffer.sampleRate;
    const samples = buffer.length;
    const bytesPerSample = 2;
    const blockAlign = numCh * bytesPerSample;
    const dataSize = samples * blockAlign;
    const bufferSize = 44 + dataSize;
    
    const ab = new ArrayBuffer(bufferSize);
    const view = new DataView(ab);
    
    const writeStr = (off, str) => {
      for (let i = 0; i < str.length; i++) view.setUint8(off + i, str.charCodeAt(i));
    };
    
    writeStr(0, 'RIFF');
    view.setUint32(4, bufferSize - 8, true);
    writeStr(8, 'WAVE');
    writeStr(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numCh, true);
    view.setUint32(24, sr, true);
    view.setUint32(28, sr * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true);
    writeStr(36, 'data');
    view.setUint32(40, dataSize, true);
    
    const chData = [];
    for (let i = 0; i < numCh; i++) chData.push(buffer.getChannelData(i));
    
    let off = 44;
    for (let i = 0; i < samples; i++) {
      for (let c = 0; c < numCh; c++) {
        const s = Math.max(-1, Math.min(1, chData[c][i]));
        view.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        off += 2;
      }
    }
    
    return ab;
  }
  
  function downloadSample(id) {
    const data = audioBuffers.get(id);
    if (!data) {
      showStatus('❌ Sample not found!', 'error');
      return;
    }
    
    try {
      let blob, filename;
      
      if (data.type === 'webm') {
        blob = data.blob;
        filename = `splice_${data.name.replace(/[^a-z0-9]/gi, '_')}_${id}.webm`;
      } else if (data.type === 'raw') {
        // Raw buffer - might be scrambled
        blob = new Blob([data.buffer], { type: 'application/octet-stream' });
        filename = `splice_${data.name.replace(/[^a-z0-9]/gi, '_')}_${id}.raw`;
        showStatus('⚠️ Raw format - may need conversion', 'waiting');
      } else {
        const wav = audioBufferToWav(data.buffer);
        blob = new Blob([wav], { type: 'audio/wav' });
        filename = `splice_${data.name.replace(/[^a-z0-9]/gi, '_')}_${id}.wav`;
      }
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      
      showStatus(`✓ Downloaded: ${data.name}`, 'success');
      
    } catch (e) {
      console.error('[Splice Downloader] Download error:', e);
      showStatus('❌ ' + e.message, 'error');
    }
  }
  
  // ========== INIT ==========
  
  function init() {
    console.log('[Splice Downloader] Initializing...');
    
    // Create UI first
    createPanel();
    
    // Then hooks
    watchForAudioElements();
    
    // Get sample info
    updateSampleInfo();
    
    // Watch URL changes
    let lastUrl = location.href;
    new MutationObserver(() => {
      if (location.href !== lastUrl) {
        lastUrl = location.href;
        setTimeout(updateSampleInfo, 500);
      }
    }).observe(document.body, { subtree: true, childList: true });
    
    // Watch play clicks
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (btn) {
        const label = btn.getAttribute('aria-label') || '';
        const svg = btn.querySelector('svg');
        if (label.toLowerCase().includes('play') || svg?.innerHTML?.includes('M8 5')) {
          console.log('[Splice Downloader] Play clicked');
          setTimeout(updateSampleInfo, 300);
        }
      }
    }, true);
    
    console.log('[Splice Downloader] ✓ Ready! Play a sample to capture.');
  }
  
  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    setTimeout(init, 100);
  }
  
})();