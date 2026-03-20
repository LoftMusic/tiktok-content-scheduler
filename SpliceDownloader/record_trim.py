"""
Audio Recorder with Auto-Trim Silence
Records from Virtual Audio Cable and automatically removes silence
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time
import sys

# Settings
SAMPLE_RATE = 44100
CHANNELS = 2
SILENCE_THRESHOLD = 0.005
MIN_SOUND_DURATION = 0.05
MIN_SILENCE_GAP = 0.2

print("=" * 50)
print("Audio Recorder - Auto Trim Silence")
print("=" * 50)

# List devices
print("\nAvailable input devices:")
for i, dev in enumerate(sd.query_devices()):
    if isinstance(dev, dict) and dev.get('max_input_channels', 0) > 0:
        print(f"  [{i}] {dev.get('name')}")

print("\n" + "=" * 50)
print("Make sure Virtual Audio Cable is set as INPUT!")
print("=" * 50)

filename = f"recording_{int(time.time())}"
print(f"\nOutput prefix: {filename}")
print("Press ENTER to start recording...")

input()

print("\n>>> RECORDING - Press ENTER to stop <<<\n")

# Record using sd.rec
max_duration = 120  # seconds
recording = np.zeros((max_duration * SAMPLE_RATE, CHANNELS), dtype=np.float32)
start_time = time.time()

try:
    # Record with sd.rec
    recording = sd.rec(int(max_duration * SAMPLE_RATE), 
                      samplerate=SAMPLE_RATE, 
                      channels=CHANNELS, 
                      dtype='float32')
    
    # Wait for user to stop
    input()
    
    # Stop recording
    sd.stop()
    
except Exception as e:
    print(f"Error: {e}")
    input()
    sys.exit(1)

# Get actual duration
actual_duration = time.time() - start_time
actual_samples = int(actual_duration * SAMPLE_RATE)
recording = recording[:actual_samples]

print(f"\nRecorded: {actual_duration:.2f} seconds")

# Convert to mono for analysis
if len(recording.shape) > 1:
    mono = np.mean(recording, axis=1)
else:
    mono = recording

# Debug
max_vol = np.max(np.abs(mono))
mean_vol = np.mean(np.abs(mono))
print(f"Max volume: {max_vol:.4f}, Mean: {mean_vol:.4f}")

if max_vol < SILENCE_THRESHOLD:
    print("No sound detected!")
    # Save raw
    wavfile.write(f"{filename}_raw.wav", SAMPLE_RATE, (recording*32767).astype(np.int16))
    print(f"Saved raw: {filename}_raw.wav")
    input("Press Enter...")
    sys.exit(0)

# Find non-silent segments
is_sound = np.abs(mono) > SILENCE_THRESHOLD
sound_indices = np.where(is_sound)[0]

if len(sound_indices) == 0:
    print("No segments found!")
    input()
    sys.exit(0)

print(f"Found {len(sound_indices)} samples above threshold")

# Find segments
segments = []
start_idx = sound_indices[0]

for i in range(1, len(sound_indices)):
    gap = sound_indices[i] - sound_indices[i-1]
    if gap > MIN_SILENCE_GAP * SAMPLE_RATE:
        end_idx = sound_indices[i-1]
        duration = (end_idx - start_idx) / SAMPLE_RATE
        if duration > MIN_SOUND_DURATION:
            segments.append((start_idx, end_idx))
        start_idx = sound_indices[i]

# Add last segment
last_duration = (sound_indices[-1] - start_idx) / SAMPLE_RATE
if last_duration > MIN_SOUND_DURATION:
    segments.append((start_idx, sound_indices[-1]))

print(f"Found {len(segments)} sound segments")

# Export each segment
for i, (start, end) in enumerate(segments):
    pad = int(0.02 * SAMPLE_RATE)
    start = max(0, start - pad)
    end = min(len(recording), end + pad)
    
    segment = recording[start:end]
    
    # Normalize
    max_val = np.max(np.abs(segment))
    if max_val > 0.01:
        segment = segment / max_val * 0.9
    
    out_file = f"{filename}_{i+1}.wav"
    wavfile.write(out_file, SAMPLE_RATE, (segment * 32767).astype(np.int16))
    
    duration = len(segment) / SAMPLE_RATE
    print(f"  Saved: {out_file} ({duration:.2f}s)")

print(f"\nDone! {len(segments)} files.")
input("Press Enter to exit...")
