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
        
        // In loop mode with BPM, align to BPM grid instead of simple silence trim
        // In oneshot mode, use the standard trim
        let processedBuffer = null;
        
        if (mode === 'loop' && settings?.bpm && settings.bpm > 0) {
          console.log('[Offscreen] Loop mode + BPM:', settings.bpm, '- applying BPM sync');
          const bars = parseInt(settings?.bars) || 4;
          const aligned = alignToBPM(audioBuffer, settings.bpm, bars, ctx);
          if (aligned) {
            console.log('[Offscreen] BPM-aligned buffer:', aligned.duration.toFixed(2), 's');
            processedBuffer = aligned;
            duration = aligned.duration;
          }
        }
        
        if (!processedBuffer) {
          // Standard silence trim for oneshot or when BPM sync fails
          const trimmed = trimSilence(audioBuffer, threshold, ctx, fadeoutMs, mode);
          if (trimmed) {
            console.log('[Offscreen] Trimmed:', trimmed.duration.toFixed(2), 's');
            processedBuffer = trimmed;
            duration = trimmed.duration;
          }
        }
        
        if (processedBuffer) {
          // Apply fadeout
          if (fadeoutMs > 0) {
            applyFadeout(processedBuffer, fadeoutMs);
          }
          
          // Convert to WAV
          const wavData = bufferToWav(processedBuffer);
          
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

/**
 * Align a loop recording to a target BPM so it locks to the grid when imported into a DAW.
 * 
 * How it works:
 * 1. Detect the first transient (onset) - where the actual audio content starts
 * 2. Find where that onset falls relative to the beat grid at the target BPM
 * 3. Calculate how much pre-roll silence is needed so the onset lands on beat 1
 * 4. Pad the beginning with silence so sample 0 = beat 1
 * 5. Trim the end to exactly N bars at the target BPM
 *
 * @param {AudioBuffer} buffer - recorded audio buffer
 * @param {number} bpm - target BPM
 * @param {number} bars - number of bars to output (2, 4, 8, or 16)
 * @param {AudioContext} ctx - AudioContext to use for creating new buffer
 * @returns {AudioBuffer|null} - new buffer aligned to BPM grid, or null on failure
 */
function alignToBPM(buffer, bpm, bars, ctx) {
  try {
    const sr = buffer.sampleRate;
    const ch = buffer.numberOfChannels;
    
    // How many seconds per beat
    const secPerBeat = 60.0 / bpm;
    // How many seconds per bar (assuming 4/4 time)
    const secPerBar = secPerBeat * 4;
    // Target length in seconds (exactly N bars)
    const targetSec = secPerBar * bars;
    // Target length in samples
    const targetSamples = Math.floor(targetSec * sr);
    
    console.log(`[BPM Align] Target: ${bpm} BPM, ${bars} bars = ${targetSec.toFixed(3)}s (${targetSamples} samples)`);
    
    // Step 1: Detect the first transient (onset)
    // Use a simple energy-based onset detection
    const onset = detectOnset(buffer);
    const onsetSec = onset / sr;
    console.log(`[BPM Align] First onset at sample ${onset} (${onsetSec.toFixed(4)}s)`);
    
    if (onset >= buffer.length - 1) {
      console.log('[BPM Align] No onset detected');
      return null;
    }
    
    // Step 2: Find where the onset falls relative to the beat grid
    // beatGridOffset = position of onset modulo one bar (in seconds)
    const beatGridOffset = onsetSec % secPerBar;
    console.log(`[BPM Align] Onset is ${beatGridOffset.toFixed(4)}s into the current bar`);
    
    // Step 3: Calculate pre-roll needed so onset lands on bar start
    // preRoll = silence needed at start so onset maps to bar start
    // If onset is 0.3s into the bar, we need 0.3s of silence before it
    const preRollSec = beatGridOffset;
    const preRollSamples = Math.floor(preRollSec * sr);
    console.log(`[BPM Align] Pre-roll: ${preRollSamples} samples (${preRollSec.toFixed(4)}s)`);
    
    // Step 4: How much content do we have after the onset?
    const contentAfterOnset = buffer.length - onset;
    const contentAfterOnsetSec = contentAfterOnset / sr;
    console.log(`[BPM Align] Content after onset: ${contentAfterOnsetSec.toFixed(3)}s`);
    
    // Step 5: Calculate total needed - pre-roll + all content after onset
    const totalNeeded = preRollSamples + contentAfterOnset;
    
    // Step 6: Trim or pad to exactly targetSamples
    // If we have more than target, trim. If less, pad with silence at end.
    let newBuffer;
    if (totalNeeded > targetSamples) {
      // Trim - cut off the end to fit exactly targetSamples
      // The end will naturally fall on a bar boundary since we're trimming content
      // beyond what fits in N bars
      console.log(`[BPM Align] Trimming ${totalNeeded - targetSamples} samples from end`);
      newBuffer = ctx.createBuffer(ch, targetSamples, sr);
      // Copy preRoll + as much content as fits
      copyBufferSection(buffer, newBuffer, onset, targetSamples - preRollSamples, 0, 0, targetSamples);
    } else {
      // Pad - add silence at the end to reach target length
      // The pre-roll is already at the start, onset falls on bar boundary,
      // and we pad the end to reach exactly N bars
      console.log(`[BPM Align] Padding end with ${targetSamples - totalNeeded} samples`);
      newBuffer = ctx.createBuffer(ch, targetSamples, sr);
      // Copy: preRoll silence + all content after onset + padding at end
      copyBufferSection(buffer, newBuffer, onset, contentAfterOnset, 0, preRollSamples, preRollSamples + contentAfterOnset);
      // Note: padding at end is implicit (newBuffer was created with zeros)
    }
    
    // Verify
    console.log(`[BPM Align] Result: ${newBuffer.duration.toFixed(3)}s (${newBuffer.length} samples), ${newBuffer.numberOfChannels}ch`);
    return newBuffer;
    
  } catch (e) {
    console.error('[BPM Align] Error:', e);
    return null;
  }
}

/**
 * Detect the first transient/onset in the audio buffer.
 * Uses a simple energy derivative approach - finds where amplitude suddenly increases.
 */
function detectOnset(buffer) {
  const ch = buffer.numberOfChannels;
  const len = buffer.length;
  const sr = buffer.sampleRate;
  
  // Compute RMS energy in small windows
  const windowSize = Math.floor(sr * 0.005); // 5ms windows
  const hopSize = Math.floor(windowSize / 2);
  const numFrames = Math.floor((len - windowSize) / hopSize);
  
  if (numFrames < 1) return 0;
  
  // RMS energy per frame
  const energy = new Float32Array(numFrames);
  for (let f = 0; f < numFrames; f++) {
    let sum = 0;
    const start = f * hopSize;
    for (let c = 0; c < ch; c++) {
      const data = buffer.getChannelData(c);
      for (let i = 0; i < windowSize; i++) {
        const idx = start + i;
        if (idx < len) {
          sum += data[idx] * data[idx];
        }
      }
    }
    energy[f] = Math.sqrt(sum / (ch * windowSize));
  }
  
  // Find the global peak energy
  let peakEnergy = 0;
  for (let f = 0; f < numFrames; f++) {
    if (energy[f] > peakEnergy) peakEnergy = energy[f];
  }
  
  // Threshold: onset must be above noise floor
  // Use 10% of peak as the minimum detectable level
  const noiseFloor = peakEnergy * 0.01; // ~-40dB from peak
  const onsetThreshold = Math.max(noiseFloor, 0.001); // absolute minimum
  
  // Find the FIRST frame where energy rises significantly above the initial level
  // (We want the very first transient, not a later loud hit)
  const initialEnergy = energy[0];
  
  // Look for a sustained rise: energy must exceed initial by at least 5x AND exceed onsetThreshold
  for (let f = 1; f < numFrames; f++) {
    const rise = energy[f] / Math.max(initialEnergy, 0.0001);
    if (rise > 5 && energy[f] > onsetThreshold) {
      // Convert frame index back to sample index
      const onsetSample = f * hopSize;
      console.log(`[Onset] Detected at frame ${f}, sample ${onsetSample}, energy ${energy[f].toFixed(5)}, rise ${rise.toFixed(1)}x`);
      return onsetSample;
    }
  }
  
  // Fallback: find first sample above a reasonable threshold
  for (let i = 0; i < len; i++) {
    let maxVal = 0;
    for (let c = 0; c < ch; c++) {
      const absVal = Math.abs(buffer.getChannelData(c)[i]);
      if (absVal > maxVal) maxVal = absVal;
    }
    if (maxVal > 0.01) {
      console.log(`[Onset] Fallback detection at sample ${i}, amplitude ${maxVal.toFixed(4)}`);
      return i;
    }
  }
  
  return 0;
}

/**
 * Copy a section from one buffer to another.
 */
function copyBufferSection(src, dst, srcStart, srcLen, dstStart, offsetIntoDst, totalDstLen) {
  const ch = src.numberOfChannels;
  for (let c = 0; c < ch; c++) {
    const srcData = src.getChannelData(c);
    const dstData = dst.getChannelData(c);
    const end = Math.min(srcStart + srcLen, src.length);
    let dstIdx = offsetIntoDst;
    for (let i = srcStart; i < end && dstIdx < dstData.length; i++, dstIdx++) {
      dstData[dstIdx] = srcData[i];
    }
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