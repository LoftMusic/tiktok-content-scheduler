"""
VST Sample Extractor
Workflow: FL Studio -> VST -> Virtual Audio Cable -> Python Recording
"""

import sounddevice as sd
import numpy as np
import os
import time

# Configuration
VST_PATH = r"C:\Program Files\VSTPlugins\BANDA CORRIDOS VST\Banda Corridos Vst.vst3"
INSTRUMENTS_DIR = r"C:\Program Files\VSTPlugins\BANDA CORRIDOS VST\Banda Corridos Vst.instruments"
OUTPUT_DIR = r"C:\Samples\BANDA_CORRIDOS_EXTRACTED"

# Virtual Audio Cable device (input)
VAC_DEVICE = 1  # Line 1 (Virtual Audio Cable), MME

# Audio settings
SAMPLE_RATE = 44100
DURATION = 3.0  # seconds per instrument
NOTES = [60, 64, 67]  # C4, E4, G4 (C major chord)

def get_instruments():
    """Get list of .mse instrument files"""
    instruments = []
    for f in os.listdir(INSTRUMENTS_DIR):
        if f.endswith('.mse'):
            instruments.append(f.replace('.mse', ''))
    return sorted(instruments)

def record_audio(duration, sample_rate, device):
    """Record audio from specified device"""
    print(f"Recording {duration}s from device {device}...")
    
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=2,
        device=device,
        dtype='float32'
    )
    
    sd.wait()
    return recording

def save_wav(filename, audio, sample_rate):
    """Save audio to WAV file"""
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.95
    
    from scipy.io import wavfile
    # Convert float32 to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, audio_int16)
    print(f"Saved: {filename}")

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get instruments
    instruments = get_instruments()
    print(f"Found {len(instruments)} instruments")
    
    print("\n=== SETUP INSTRUCTIONS ===")
    print("1. Open FL Studio")
    print("2. Add VST: BANDA CORRIDOS VST")
    print("3. Set FL Studio audio output to: Virtual Audio Cable")
    print("4. Set MIDI input to: Your MIDI controller (or use piano roll)")
    print("5. Press PLAY on first instrument, then RUN this script")
    print("\nThe script will record 3 seconds per instrument.")
    print("After recording each instrument, change to the next program in VST.")
    print("================================\n")
    
    input("Press ENTER when ready...")
    
    # Record each instrument
    for i, instrument in enumerate(instruments):
        print(f"\n[{i+1}/{len(instruments)}] Recording: {instrument}")
        print("-> Switch VST to this instrument, then press ENTER...")
        input()
        
        audio = record_audio(DURATION, SAMPLE_RATE, VAC_DEVICE)
        
        # Save
        filename = os.path.join(OUTPUT_DIR, f"{instrument}.wav")
        save_wav(filename, audio, SAMPLE_RATE)
    
    print(f"\nDone! All samples saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
