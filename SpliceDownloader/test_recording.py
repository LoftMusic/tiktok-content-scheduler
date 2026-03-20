import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time

SAMPLE_RATE = 44100
CHANNELS = 2

print("=" * 50)
print("Testing Recording")
print("=" * 50)

# Show available input devices
print("\nAvailable input devices:")
for i, dev in enumerate(sd.query_devices()):
    if isinstance(dev, dict) and dev.get('max_input_channels', 0) > 0:
        print(f"  [{i}] {dev['name']} (channels: {dev['max_input_channels']})")

# Get default input
default_input = sd.query_devices(kind='input')
print(f"\nDefault input device: {default_input['name']}")
print(f"Device index: {default_input['index']}")

print("\n" + "=" * 50)
print("START PLAYING AUDIO NOW!")
print("Recording for 5 seconds...")
print("=" * 50)

# Record
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
    filename = f"test_rec_{int(time.time())}.wav"
    wavfile.write(filename, SAMPLE_RATE, (recording * 32767).astype(np.int16))
    print(f"✅ Saved: {filename}")
else:
    print("❌ No audio detected!")
    print("\nPossible causes:")
    print("1. No audio playing through system")
    print("2. VAC not set as default recording device")
    print("3. No loopback from UA to VAC")
