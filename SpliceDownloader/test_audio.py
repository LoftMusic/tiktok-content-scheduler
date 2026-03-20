"""
Quick Audio Device Test
Tests if audio input is working
"""

import sounddevice as sd
import numpy as np

print("Audio Input Test")
print("=" * 40)

print("\nListening for 3 seconds...")
print("Make some noise!")

# Record for 3 seconds
recording = sd.rec(int(3 * 44100), samplerate=44100, channels=1, dtype='float32')
sd.wait()

# Check volume
max_vol = np.max(np.abs(recording))
mean_vol = np.mean(np.abs(recording))

print(f"\nMax volume: {max_vol:.4f}")
print(f"Mean volume: {mean_vol:.4f}")

if max_vol > 0.01:
    print("\n✅ Audio input is WORKING!")
else:
    print("\n❌ No audio detected!")
    print("Check your input device settings.")

print("\nPress Enter to exit...")
input()
