import sounddevice as sd
import numpy as np
import soundfile as sf
import sys, os, time

print(f"Python: {sys.version}")
print(f"sounddevice: {sd.__version__}")

# Find Volt loopback - try all device indices, including output-only as potential recording sources
target_dev = None
target_name = None

# Check all devices that might be loopback (output devices from volt)
for i, d in enumerate(sd.query_devices()):
    name = d.get('name', '')
    print(f"[{i}] {name} | inputs:{d.get('max_input_channels')} outputs:{d.get('max_output_channels')} hostapi:{d.get('hostapi')}")
    if 'volt' in name.lower() and 'monitor' in name.lower():
        target_dev = i
        target_name = name
        print(f"  ^ Found Volt MONITOR")

# Try recording from the MONITOR device directly (even if it shows 0 input channels)
if target_dev is not None:
    dev_info = sd.query_devices(target_dev)
    print(f"\nTarget device info: {dev_info}")
    print(f"Recording from device {target_dev} ('{target_name}')...")
    try:
        # Check what APIs support recording from this device
        print("\nTrying to record from MONITOR as input...")
        # Some devices accept input even if max_input_channels=0 in listing
        recording = sd.rec(
            frames=3 * 44100,
            samplerate=44100,
            channels=2,
            device=target_dev,
            dtype='float32',
            extra_settings=None
        )
        print("Recording started...")
        sd.wait()
        print(f"Recording done, shape: {recording.shape}, dtype: {recording.dtype}")
        max_amp = np.abs(recording).max()
        print(f"Max amplitude: {max_amp:.4f}")
        
        if max_amp > 0.001:
            out_path = r"C:\Users\Studio3\Desktop\test_loopback_sd.wav"
            sf.write(out_path, recording, 44100)
            print(f"Saved: {out_path}")
        else:
            print("Recording is silent!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No Volt MONITOR found")
