// Offscreen document - captures and processes audio

let mediaRecorder = null;
let audioChunks = [];
let audioStream = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Offscreen] Message:', message.type);
  
  if (message.type === 'startCapture') {
    startCapture(message.streamId, message.settings)
      .then(() => sendResponse({ success: true }))
      .catch(err => {
        console.error('[Offscreen] Start error:', err);
        sendResponse({ success: false, error: String(err) });
      });
    return true;
  }
  
  if (message.type === 'stopCapture') {
    stopCapture(message.settings)
      .then(result => sendResponse(result))
      .catch(err => {
        console.error('[Offscreen] Stop error:', err);
        sendResponse({ success: false, error: String(err) });
      });
    return true;
  }
});

async function startCapture(streamId, settings) {
  console.log('[Offscreen] startCapture:', streamId);
  
  try {
    audioStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        mandatory: {
          chromeMediaSource: 'tab',
          chromeMediaSourceId: streamId
        }
      },
      video: false
    });
    
    console.log('[Offscreen] Stream obtained');
    
    mediaRecorder = new MediaRecorder(audioStream, {
      mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus' 
        : 'audio/webm'
    });
    
    audioChunks = [];
    
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        audioChunks.push(e.data);
      }
    };
    
    mediaRecorder.start(100);
    console.log('[Offscreen] Recording started');
    
    const maxMs = (settings?.maxDuration || 30) * 1000;
    setTimeout(async () => {
      if (mediaRecorder?.state === 'recording') {
        console.log('[Offscreen] Auto-stop');
        await stopCapture(settings);
      }
    }, maxMs);
    
  } catch (err) {
    console.error('[Offscreen] Start failed:', err);
    throw err;
  }
}

async function stopCapture(settings) {
  console.log('[Offscreen] stopCapture');
  
  return new Promise((resolve) => {
    if (!mediaRecorder || mediaRecorder.state !== 'recording') {
      resolve({ success: false, error: 'Not recording' });
      return;
    }
    
    mediaRecorder.onstop = async () => {
      console.log('[Offscreen] Recorder stopped');
      
      if (audioStream) {
        audioStream.getTracks().forEach(t => t.stop());
        audioStream = null;
      }
      
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      console.log('[Offscreen] Blob size:', blob.size, 'bytes');
      
      if (blob.size < 1000) {
        resolve({ success: false, error: 'Recording too short' });
        return;
      }
      
      // Try to process (trim), fall back to raw
      const result = await processAudio(blob, settings);
      resolve(result);
      
      mediaRecorder = null;
      audioChunks = [];
    };
    
    mediaRecorder.stop();
  });
}

async function processAudio(blob, settings) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const mode = settings?.mode || 'oneshot';
  const cat = settings?.category || 'other';
  const name = settings?.filename || `sample_${ts}`;
  
  console.log('[Offscreen] processAudio settings:', JSON.stringify(settings));
  console.log('[Offscreen] Using filename:', name, 'category:', cat);
  
  const threshold = settings?.threshold || -40;
  
  // Try to trim and convert to WAV
  let processedData = null;
  let duration = 0;
  let format = 'webm';
  const fadeoutMs = settings?.fadeout || 50; // Fadeout duration in ms
  
  try {
    // Check if AudioContext is available
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    
    if (AudioContextClass) {
      console.log('[Offscreen] Attempting WAV conversion...');
      
      const ctx = new AudioContextClass();
      const arrayBuffer = await blob.arrayBuffer();
      
      try {
        const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
        console.log('[Offscreen] Decoded:', audioBuffer.duration.toFixed(2), 's');
        duration = audioBuffer.duration;
        
        // Trim silence
        const trimmed = trimSilence(audioBuffer, threshold, ctx, fadeoutMs, mode);
        
        if (trimmed) {
          console.log('[Offscreen] Trimmed:', trimmed.duration.toFixed(2), 's');
          duration = trimmed.duration;
          
          // Convert to WAV
          const wavData = bufferToWav(trimmed);
          
          // Convert to base64
          const base64 = arrayBufferToBase64(wavData);
          processedData = 'data:audio/wav;base64,' + base64;
          format = 'wav';
          
          console.log('[Offscreen] WAV created:', wavData.byteLength, 'bytes');
        }
        
        ctx.close();
      } catch (e) {
        console.log('[Offscreen] AudioContext failed:', e.message);
        ctx.close();
      }
    }
  } catch (e) {
    console.log('[Offscreen] Processing failed:', e.message);
  }
  
  // Fall back to raw WebM if processing failed
  if (!processedData) {
    console.log('[Offscreen] Using raw WebM');
    const arrayBuffer = await blob.arrayBuffer();
    const base64 = arrayBufferToBase64(arrayBuffer);
    processedData = 'data:audio/webm;base64,' + base64;
  }
  
  // Send to background for download - split by mode (oneshot/loop) then category
  const filename = `Audio/splice_samples/${mode}/${cat}/${name}.${format}`;
  
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'saveAudio',
      data: processedData,
      filename: filename
    });
    
    if (response.success) {
      return {
        success: true,
        filename: `${name}.${format}`,
        filepath: filename,
        duration: duration,
        format: format
      };
    } else {
      return { success: false, error: response.error };
    }
  } catch (err) {
    console.error('[Offscreen] Send error:', err);
    return { success: false, error: String(err) };
  }
}

function trimSilence(buffer, thresholdDb, ctx, fadeoutMs, mode) {
  try {
    mode = mode || 'oneshot';
    const ch = buffer.numberOfChannels;
    const len = buffer.length;
    const sr = buffer.sampleRate;

    // Find amplitude envelope
    const amp = new Float32Array(len);
    let peakVal = 0;
    for (let c = 0; c < ch; c++) {
      const data = buffer.getChannelData(c);
      for (let i = 0; i < len; i++) {
        const absVal = Math.abs(data[i]);
        amp[i] = Math.max(amp[i], absVal);
        if (absVal > peakVal) peakVal = absVal;
      }
    }

    if (peakVal === 0) {
      console.log('[Offscreen] No audio found');
      return null;
    }

    // Use peak-relative threshold: -12dB from peak for cleaner release detection
    // Peak-relative adapts to the sample's own dynamics rather than a fixed dB floor
    const peakThreshold = peakVal * 0.251; // ~-12dB from peak
    const absThreshold = Math.pow(10, thresholdDb / 20);

    // Use whichever threshold is LOWER (less aggressive) so we don't over-trim quiet releases
    // But also enforce a minimum floor so we don't chase the noise floor
    const threshold = Math.max(Math.min(peakThreshold, absThreshold), 0.001);

    // Find start - first sample above threshold
    let start = 0;
    for (let i = 0; i < len; i++) {
      if (amp[i] > threshold) { start = i; break; }
    }

    // Find end - last sample above threshold
    let end = len - 1;
    for (let i = len - 1; i >= 0; i--) {
      if (amp[i] > threshold) { end = i; break; }
    }

    if (mode === 'oneshot') {
      // Oneshot: shift end point 50ms to the right to preserve full release tail
      // This ensures we don't cut into the sound's natural decay
      const endShiftMs = 50;
      const endShiftSamples = Math.floor(sr * endShiftMs / 1000);
      end = Math.min(len - 1, end + endShiftSamples);
    } else {
      // Loop mode: use standard padding (50ms at end)
      const padEnd = Math.floor(sr * 0.05);
      end = Math.min(len - 1, end + padEnd);
    }

    if (start >= end) {
      console.log('[Offscreen] No audio above threshold');
      return null;
    }

    const newLen = end - start + 1;
    const newBuf = ctx.createBuffer(ch, newLen, sr);

    for (let c = 0; c < ch; c++) {
      const src = buffer.getChannelData(c);
      const dst = newBuf.getChannelData(c);
      for (let i = 0; i < newLen; i++) {
        dst[i] = src[start + i];
      }
    }

    // Apply fadeout
    if (fadeoutMs > 0) {
      applyFadeout(newBuf, fadeoutMs);
    }

    return newBuf;
  } catch (e) {
    console.error('[Offscreen] trimSilence error:', e);
    return null;
  }
}

function applyFadeout(buffer, fadeMs) {
  const sr = buffer.sampleRate;
  const fadeSamples = Math.floor(sr * fadeMs / 1000);
  const ch = buffer.numberOfChannels;
  const len = buffer.length;
  
  if (fadeSamples >= len) return; // Don't fade if audio is too short
  
  for (let c = 0; c < ch; c++) {
    const data = buffer.getChannelData(c);
    for (let i = 0; i < fadeSamples; i++) {
      // Fade out curve (exponential)
      const idx = len - fadeSamples + i;
      if (idx >= 0 && idx < len) {
        const fadeAmount = 1 - (i / fadeSamples);
        const curve = fadeAmount * fadeAmount; // Quadratic for smoother
        data[idx] *= curve;
      }
    }
  }
}

function bufferToWav(buffer) {
  const ch = buffer.numberOfChannels;
  const sr = buffer.sampleRate;
  const samples = buffer.length;
  const bytesPerSample = 2;
  const blockAlign = ch * bytesPerSample;
  const dataSize = samples * blockAlign;
  const fileSize = 44 + dataSize;
  
  const ab = new ArrayBuffer(fileSize);
  const v = new DataView(ab);
  
  // WAV header
  writeString(v, 0, 'RIFF');
  v.setUint32(4, fileSize - 8, true);
  writeString(v, 8, 'WAVE');
  writeString(v, 12, 'fmt ');
  v.setUint32(16, 16, true);
  v.setUint16(20, 1, true);
  v.setUint16(22, ch, true);
  v.setUint32(24, sr, true);
  v.setUint32(28, sr * blockAlign, true);
  v.setUint16(32, blockAlign, true);
  v.setUint16(34, 16, true);
  writeString(v, 36, 'data');
  v.setUint32(40, dataSize, true);
  
  // Audio data (interleaved)
  for (let c = 0; c < ch; c++) {
    const data = buffer.getChannelData(c);
    let offset = 44 + c * bytesPerSample;
    for (let i = 0; i < samples; i++) {
      const sample = Math.max(-1, Math.min(1, data[i]));
      const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
      v.setInt16(offset, intSample, true);
      offset += blockAlign;
    }
  }
  
  return ab;
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

function arrayBufferToBase64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

console.log('[Offscreen] Ready');