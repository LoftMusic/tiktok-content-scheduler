"""
Audio Recorder - System Audio via WASAPI
Records what you hear (system audio), not microphone
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time
import sys

SAMPLE_RATE = 44100
CHANNELS = 2
SILENCE_THRESHOLD = 0.003
MIN_SOUND_DURATION = 0.05
MIN_SILENCE_GAP = 0.2

print("=" * 50)
print("System Audio Recorder - WASAPI")
print("=" * 50)

# List devices
print("\nAudio devices:")
for i, dev in enumerate(sd.query_devices()):
    if isinstance(dev, dict):
        in_ch = dev.get('max_input_channels', 0)
        out_ch = dev.get('max_output_channels', 0)
        name = dev.get('name', 'Unknown')
        if in_ch > 0 or out_ch > 0:
            ch_info = f"IN:{in_ch}" if in_ch > 0 else f"OUT:{out_ch}"
            print(f"  [{i}] {name} ({ch_info})")

print("\n" + "=" * 50)

filename = f"recording_{int(time.time())}"
print(f"Output: {filename}_*.wav")
print("Press ENTER to start recording...")

input()

print("\n>>> RECORDING - Press ENTER to stop <<<\n")

# Record
try:
    recording = sd.rec(int(120 * SAMPLE_RATE), 
                      samplerate=SAMPLE_RATE, 
                      channels=CHANNELS, 
                      dtype='float32')
    input()
    sd.stop()
except Exception as e:
    print(f"Error: {e}")
    input()
    sys.exit(1)

actual = int(sd.recording_duration * SAMPLE_RATE)
recording = recording[:actual]
print(f"Recorded: {actual/SAMPLE_RATE:.2f}s")

# Mono for analysis
mono = np.mean(recording, axis=1) if len(recording.shape) > 1 else recording

max_vol = np.max(np.abs(mono))
print(f"Max volume: {max_vol:.4f}")

if max_vol < SILENCE_THRESHOLD:
    print("No sound detected!")
    # Save raw
    wavfile.write(f"{filename}_raw.wav", SAMPLE_RATE, (recording*32767).astype(np.int16))
    print(f"Saved raw: {filename}_raw.wav")
    input()
    sys.exit(0)

# Find segments
is_sound = np.abs(mono) > SILENCE_THRESHOLD
indices = np.where(is_sound)[0]

if len(indices) == 0:
    print("No segments!")
    input()
    sys.exit(0)

segments = []
start = indices[0]

for i in range(1, len(indices)):
    if indices[i] - indices[i-1] > MIN_SILENCE_GAP * SAMPLE_RATE:
        if (indices[i-1] - start) / SAMPLE_RATE > MIN_SOUND_DURATION:
            segments.append((start, indices[i-1]))
        start = indices[i]

if (indices[-1] - start) / SAMPLE_RATE > MIN_SOUND_DURATION:
    segments.append((start, indices[-1]))

print(f"Found {len(segments)} segments")

# Export
for i, (s, e) in enumerate(segments):
    pad = int(0.02 * SAMPLE_RATE)
    s, e = max(0, s-pad), min(len(recording), e+pad)
    
    seg = recording[s:e]
    maxv = np.max(np.abs(seg))
    if maxv > 0.01:
        seg = seg / maxv * 0.9
    
    out = f"{filename}_{i+1}.wav"
    wavfile.write(out, SAMPLE_RATE, (seg*32767).astype(np.int16))
    print(f"  Saved: {out} ({len(seg)/SAMPLE_RATE:.2f}s)")

print(f"\nDone! {len(segments)} files.")
input()
