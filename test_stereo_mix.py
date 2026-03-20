import sounddevice as sd
import numpy as np
import soundfile as sf
import sys, os, time

print(f"sounddevice {sd.__version__}")

# Test recording from Stereo Mix (device 29, hostapi 3 = WDM-KS)
# This is a WDM-KS device that typically captures system audio
print("\n=== Test: Stereo Mix (Realtek HD Audio) ===")
print("Recording 5 seconds from Stereo Mix (device 29)...")
try:
    recording = sd.rec(
        frames=5 * 44100,
        samplerate=44100,
        channels=2,
        device=29,  # Stereo Mix (Realtek HD Audio Stereo input)
        dtype='float32'
    )
    sd.wait()
    max_amp = np.abs(recording).max()
    print(f"Max amplitude: {max_amp:.6f}")
    if max_amp > 0.001:
        out = r"C:\Users\Studio3\Desktop\test_stereo_mix.wav"
        sf.write(out, recording, 44100)
        print(f"Saved: {out}")
    else:
        print("Silent - Stereo Mix not capturing system audio")
except Exception as e:
    print(f"Error: {e}")

# Also test recording from device 9 (Primary Sound Capture Driver, WASAPI)
print("\n=== Test: Primary Sound Capture Driver (device 9, hostapi 1 = DirectSound) ===")
try:
    recording2 = sd.rec(
        frames=5 * 44100,
        samplerate=44100,
        channels=2,
        device=9,
        dtype='float32'
    )
    sd.wait()
    max_amp2 = np.abs(recording2).max()
    print(f"Max amplitude: {max_amp2:.6f}")
    if max_amp2 > 0.001:
        out2 = r"C:\Users\Studio3\Desktop\test_primary_capture.wav"
        sf.write(out2, recording2, 44100)
        print(f"Saved: {out2}")
    else:
        print("Silent")
except Exception as e:
    print(f"Error: {e}")
