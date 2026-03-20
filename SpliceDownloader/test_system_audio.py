"""
Audio Recorder - Record SYSTEM AUDIO (not microphone)
Uses Windows Stereo Mix or WASAPI loopback
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time
import os
import sys

SAMPLE_RATE = 44100
CHANNELS = 2
SILENCE_THRESHOLD = 0.005
MIN_SOUND_DURATION = 0.05
MIN_SILENCE_GAP = 0.2

print("=" * 50)
print("Audio Recorder - System Audio (WASAPI/Stereo Mix)")
print("=" * 50)

# List ALL audio devices
print("\n=== ALL AUDIO DEVICES ===")
all_devices = sd.query_devices()
print(f"Total devices: {len(all_devices) if isinstance(all_devices, list) else 'single'}")

# Try to find loopback/Stereo Mix devices
loopback_devices = []
for i, dev in enumerate(all_devices):
    if isinstance(dev, dict):
        name = dev.get('name', '').lower()
        # Check for loopback, stereo mix, or virtual cable
        if any(x in name for x in ['loopback', 'stereo mix', 'virtual audio', 'cable', 'wasapi']):
            if dev.get('max_input_channels', 0) > 0:
                loopback_devices.append((i, dev.get('name'), dev.get('max_input_channels')))
                print(f"  [{i}] {dev.get('name')} - {dev.get('max_input_channels')}ch (INPUT)")

# Also show output devices that could be loopback
print("\n=== OUTPUT DEVICES (may work as loopback) ===")
for i, dev in enumerate(all_devices):
    if isinstance(dev, dict) and dev.get('max_output_channels', 0) > 0:
        name = dev.get('name', '').lower()
        print(f"  [{i}] {dev.get('name')} - {dev.get('max_output_channels')}ch OUTPUT")

# Try to use default loopback or WASAPI
print("\n=== TRYING TO RECORD ===")

# Method 1: Try using default device with loopback
try:
    print("\nMethod 1: Using default device with extra settings...")
    # Use default input device
    device_info = sd.query_devices(kind='input')
    print(f"Default input: {device_info.get('name')}")
    
    print("\nRecording for 5 seconds...")
    print("PLAY AUDIO NOW!")
    
    recording = sd.rec(int(5 * SAMPLE_RATE), 
                      samplerate=SAMPLE_RATE, 
                      channels=CHANNELS, 
                      dtype='float32',
                      blocking=True)
    
    max_vol = np.max(np.abs(recording))
    print(f"Max volume: {max_vol:.4f}")
    
    if max_vol > 0.01:
        print("✅ SUCCESS! Recording system audio works!")
        filename = f"system_test_{int(time.time())}.wav"
        wavfile.write(filename, SAMPLE_RATE, (recording * 32767).astype(np.int16))
        print(f"Saved: {filename}")
    else:
        print("❌ No audio - try a different device")
        
except Exception as e:
    print(f"Error: {e}")

# Method 2: Try specific loopback device
print("\n" + "=" * 50)
print("Method 2: Trying Virtual Audio Cable directly...")

try:
    # Try to find Virtual Audio Cable
    for i, dev in enumerate(all_devices):
        if isinstance(dev, dict):
            name = dev.get('name', '').lower()
            if 'virtual' in name and 'audio' in name:
                print(f"Found: {dev.get('name')} at index {i}")
                
                print("Recording 5 seconds from Virtual Audio Cable...")
                recording = sd.rec(int(5 * SAMPLE_RATE),
                                 samplerate=SAMPLE_RATE,
                                 channels=CHANNELS,
                                 dtype='float32',
                                 device=i,
                                 blocking=True)
                
                max_vol = np.max(np.abs(recording))
                print(f"Max volume: {max_vol:.4f}")
                
                if max_vol > 0.01:
                    print("✅ SUCCESS!")
                    filename = f"vac_test_{int(time.time())}.wav"
                    wavfile.write(filename, SAMPLE_RATE, (recording * 32767).astype(np.int16))
                    print(f"Saved: {filename}")
                break
                
except Exception as e:
    print(f"Error: {e}")

print("\n=== INSTRUCTIONS ===")
print("To record system audio:")
print("1. Set Virtual Audio Cable as input device in Windows")
print("2. OR enable Stereo Mix in Windows Sound settings")
print("3. Then run record_system.py")

input("\nPress Enter to exit...")
