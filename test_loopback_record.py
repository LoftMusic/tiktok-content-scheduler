import sounddevice as sd
import numpy as np
import soundfile as sf
import sys, os, time

print(f"Python: {sys.version}")
print(f"sounddevice: {sd.__version__}")

# List all audio devices
print("\n=== All devices ===")
devices = sd.query_devices()
for i, d in enumerate(devices):
    print(f"[{i}] {d}")

# Find loopback devices
print("\n=== Loopback devices ===")
loopback = []
for i, d in enumerate(devices):
    if d.get('max_input_channels', 0) > 0 and 'loopback' in d.get('name', '').lower():
        loopback.append((i, d))
    elif d.get('max_output_channels', 0) > 0 and 'loopback' in d.get('name', '').lower():
        loopback.append((i, d))

if loopback:
    for i, d in loopback:
        print(f"  [{i}] {d}")
else:
    print("  No loopback devices found")

# Try to record from the first loopback device for 3 seconds
# Find any device with "Volt" and "loopback"
print("\n=== Test recording from Volt loopback ===")
target_dev = None
for i, d in enumerate(devices):
    name = d.get('name', '')
    if 'volt' in name.lower() and 'loopback' in name.lower():
        target_dev = i
        print(f"Found: [{i}] {d}")
        break

if target_dev is None:
    # Try any loopback
    for i, d in enumerate(devices):
        if d.get('max_input_channels', 0) > 0 and 'loopback' in d.get('name', '').lower():
            target_dev = i
            print(f"Using loopback device: [{i}] {d}")
            break

if target_dev is not None:
    print(f"\nRecording 3 seconds from device {target_dev}...")
    try:
        # Record with loopback device
        recording = sd.rec(
            frames=3 * 44100,
            samplerate=44100,
            channels=2,
            device=target_dev,
            dtype='float32'
        )
        print("Recording started, waiting...")
        sd.wait()
        print(f"Recording done, shape: {recording.shape}")

        # Save
        out_path = r"C:\Users\Studio3\Desktop\test_loopback_recording.wav"
        sf.write(out_path, recording, 44100)
        size = os.path.getsize(out_path)
        print(f"Saved to {out_path} ({size} bytes)")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No loopback device found!")
