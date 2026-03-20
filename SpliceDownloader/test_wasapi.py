"""
Audio Recorder - System Audio via WASAPI
Records what you hear, not microphone
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time

SAMPLE_RATE = 44100
CHANNELS = 2

print("=" * 50)
print("System Audio Recorder (WASAPI)")
print("=" * 50)

print("\nLooking for audio devices...")

# Find WASAPI devices
wasapi_devices = []
for i, dev in enumerate(sd.query_devices()):
    if isinstance(dev, dict):
        name = dev.get('name', '').lower()
        if 'wasapi' in name or 'loopback' in name or 'virtual' in name:
            wasapi_devices.append((i, dev.get('name'), dev))

# Also check default
default = sd.query_devices(kind='input')
print(f"Default input: {default.get('name')}")

if wasapi_devices:
    print("\nFound WASAPI/Loopback devices:")
    for idx, name, _ in wasapi_devices:
        print(f"  [{idx}] {name}")
else:
    print("\nNo WASAPI loopback found.")
    print("Make sure Virtual Audio Cable is installed.")

print("\n" + "=" * 50)
print("Testing recording...")
print("PLAY AUDIO NOW!")
print("=" * 50)

# Try default first
try:
    # Record 5 seconds
    recording = sd.rec(
        int(5 * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32',
        blocking=True
    )
    
    max_vol = np.max(np.abs(recording))
    print(f"\nMax volume: {max_vol:.4f}")
    
    if max_vol > 0.001:
        print("✅ Works! Recording system audio.")
        wavfile.write("test_output.wav", SAMPLE_RATE, (recording * 32767).astype(np.int16))
        print("Saved: test_output.wav")
    else:
        print("❌ No audio detected.")
        print("Check: Windows Sound → Input = Virtual Audio Cable")
        
except Exception as e:
    print(f"Error: {e}")

input("\nPress Enter...")
