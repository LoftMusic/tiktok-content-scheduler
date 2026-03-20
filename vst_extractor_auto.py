"""
VST Sample Extractor - Auto Mode
Records all instruments in sequence automatically
"""

import sounddevice as sd
import numpy as np
import os
import time
from scipy.io import wavfile

# Configuration
OUTPUT_DIR = r"C:\Samples\BANDA_CORRIDOS_EXTRACTED"
VAC_DEVICE = 1  # Virtual Audio Cable input
SAMPLE_RATE = 44100
DURATION = 3.0  # seconds per instrument

# Instrument list (from earlier scan)
INSTRUMENTS = [
    "ACORDEON DE SINALOA",
    "ARPA GRANDE",
    "BAJO ELECTRICO",
    "BAJO QUINTETO",
    "CONGAS",
    "GUITARRA CORRIDOS",
    "GUITARRA PACO",
    "GUITARRA PETE",
    "GUITARRA SAX",
    "LET HER GO GUITAR",
    "OUD WORLD",
    "PIANO CORRIDOS",
    "SALAMOX",
    "TAMBORA",
    "TARIMA",
    "TUBULAR BELLS",
    "VIBRAPHONE JAZZ",
    "VIOLIN CORRIDOS",
    "VIOLIN LEAD",
    "VIOLIN SAX",
    "VIOLIN STRIPPED",
    "VIOLIN SYNTH",
    "VIOLIN TREMOLO"
]

def record_audio(duration, sample_rate, device):
    """Record audio from specified device"""
    print(f"Recording {duration}s...", end=" ", flush=True)
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=2,
        device=device,
        dtype='float32'
    )
    sd.wait()
    print("Done!")
    return recording

def save_wav(filename, audio):
    """Save audio to WAV file"""
    audio = audio / np.max(np.abs(audio) + 0.001) * 0.95
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filename, SAMPLE_RATE, audio_int16)

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 50)
    print("VST Sample Extractor - AUTO MODE")
    print("=" * 50)
    print(f"\nFound {len(INSTRUMENTS)} instruments")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Device: Virtual Audio Cable (#{VAC_DEVICE})")
    print(f"Duration: {DURATION}s per instrument")
    print("\n" + "=" * 50)
    print("SETUP:")
    print("1. Open FL Studio")
    print("2. Add VST: BANDA CORRIDOS VST")  
    print("3. Audio Output: Virtual Audio Cable")
    print("4. In VST: Select FIRST instrument")
    print("5. Press ENTER to start recording...")
    print("=" * 50 + "\n")
    
    # Check audio device
    try:
        dev_info = sd.query_devices(VAC_DEVICE)
        print(f"Audio device OK: {dev_info['name']}")
    except:
        print(f"ERROR: Device {VAC_DEVICE} not found!")
        print("Available input devices:")
        for i in range(sd.device_count()):
            d = sd.query_devices(i)
            if d['max_input_channels'] > 0:
                print(f"  {i}: {d['name']}")
        return
    
    print("\nStarting in 5 seconds...")
    print("Make sure VST is playing the first instrument!")
    time.sleep(5)
    
    # Auto-record all instruments
    for i, instrument in enumerate(INSTRUMENTS):
        print(f"\n[{i+1}/{len(INSTRUMENTS)}] {instrument}")
        
        # Record
        audio = record_audio(DURATION, SAMPLE_RATE, VAC_DEVICE)
        
        # Save
        filename = os.path.join(OUTPUT_DIR, f"{instrument}.wav")
        save_wav(filename, audio)
        
        print(f"  Saved: {filename}")
        
        # Wait a bit between instruments
        print("  Next instrument...", end=" ", flush=True)
        time.sleep(1)
        print("OK")
    
    print("\n" + "=" * 50)
    print("DONE! All samples extracted to:")
    print(OUTPUT_DIR)
    print("=" * 50)

if __name__ == "__main__":
    main()
