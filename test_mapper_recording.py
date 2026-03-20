import sounddevice as sd
import numpy as np
import soundfile as sf
import sys, os

print(f"sounddevice {sd.__version__}")

# Try recording from the Microsoft Sound Mapper - this should capture whatever
# the Windows default playback device is outputting
mapper_info = sd.query_devices(0)
print(f"\nDevice 0: {mapper_info}")

# Also check if there are any WASAPI-specific loopback devices
print("\nSearching for devices with loopback capability...")
for i, d in enumerate(sd.query_devices()):
    name = d.get('name', '')
    if any(x in name.lower() for x in ['monitor', 'loopback', 'stereo mix']):
        print(f"  [{i}] {name} | inputs:{d.get('max_input_channels')} outputs:{d.get('max_output_channels')} hostapi:{d.get('hostapi')}")

# Try recording from device 0 (Microsoft Sound Mapper - Input) for 5 seconds
print("\n=== Test: Recording from Microsoft Sound Mapper (device 0) ===")
print("Please play the WAV file on Splice app NOW...")
print("Recording in 2 seconds...")
import time
time.sleep(2)

try:
    print("Recording 5 seconds...")
    recording = sd.rec(
        frames=5 * 44100,
        samplerate=44100,
        channels=2,
        device=0,  # Microsoft Sound Mapper - Input
        dtype='float32'
    )
    sd.wait()
    print(f"Done, shape: {recording.shape}, dtype: {recording.dtype}")
    max_amp = np.abs(recording).max()
    print(f"Max amplitude: {max_amp:.6f}")
    
    if max_amp > 0.001:
        out_path = r"C:\Users\Studio3\Desktop\test_mapper_recording.wav"
        sf.write(out_path, recording, 44100)
        print(f"Saved: {out_path}")
    else:
        print("Recording is silent - system audio may not be going through the mapper")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
