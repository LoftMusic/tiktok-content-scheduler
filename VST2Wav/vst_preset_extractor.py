"""
VST Preset Extractor
Extracts all presets with all MIDI notes (or single note)
Saves as: PRESET_NAME_NOTE.wav
"""

import sounddevice as sd
import numpy as np
import os
import time
from scipy.io import wavfile
import mido
from mido import Message

# Configuration
OUTPUT_DIR = r"C:\Samples\BANDA_CORRIDOS_PRESETS"
VAC_DEVICE = 1  # Virtual Audio Cable
SAMPLE_RATE = 44100
NOTE_DURATION = 0.5  # seconds per note
NOTE_VELOCITY = 100
SILENCE_THRESHOLD = 0.01

# MIDI note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Presets list (from .mse files)
PRESETS = [
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

# Notes to play per preset (empty = all 128, or specify list)
# Example: NOTES_TO_PLAY = [60]  (only C4)
# Example: NOTES_TO_PLAY = [48, 60, 72]  (C3, C4, C5)
NOTES_TO_PLAY = []  # Empty = all 128 notes

# MIDI channel (0-15)
MIDI_CHANNEL = 0

def midi_to_note_name(midi_num):
    """Convert MIDI number to note name (C-1 to G8)"""
    octave = (midi_num // 12) - 1
    note = NOTE_NAMES[midi_num % 12]
    return f"{note}{octave}"

def note_name_to_filename(note_name):
    """Convert note name to safe filename"""
    return note_name.replace('#', 's')

def safe_filename(name):
    """Make filename safe"""
    return name.replace(' ', '_').replace('#', 's').replace('\\', '').replace('/', '')

def get_midi_output():
    """Find loopMIDI port"""
    ports = mido.get_output_names()
    for port in ports:
        if 'loop' in port.lower():
            return port
    return ports[0] if ports else None

def send_program_change(port, program_num, channel=0):
    """Send MIDI Program Change"""
    if port:
        try:
            with mido.open_output(port) as midi_out:
                msg = Message('program_change', program=program_num, channel=channel)
                midi_out.send(msg)
                time.sleep(0.1)  # Wait for VST to load preset
        except Exception as e:
            print(f"Program Change Error: {e}")

def send_note_on(port, note, velocity, channel=0):
    """Send Note On"""
    if port:
        try:
            with mido.open_output(port) as midi_out:
                msg = Message('note_on', note=note, velocity=velocity, channel=channel)
                midi_out.send(msg)
        except Exception as e:
            print(f"Note On Error: {e}")

def send_note_off(port, note, channel=0):
    """Send Note Off"""
    if port:
        try:
            with mido.open_output(port) as midi_out:
                msg = Message('note_off', note=note, velocity=0, channel=channel)
                midi_out.send(msg)
        except Exception as e:
            print(f"Note Off Error: {e}")

def record_audio(duration, sample_rate, device):
    """Record audio from specified device"""
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=2,
        device=device,
        dtype='float32'
    )
    sd.wait()
    return recording

def is_silent(audio, threshold=0.01):
    """Check if audio is silent"""
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    return np.max(np.abs(audio)) < threshold

def save_wav(filename, audio):
    """Save audio to WAV file"""
    max_val = np.max(np.abs(audio))
    if max_val > 0.01:
        audio = audio / max_val * 0.9
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filename, SAMPLE_RATE, audio_int16)

def main():
    print("=" * 60)
    print("VST Preset Extractor")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Determine notes to play
    if NOTES_TO_PLAY:
        notes = NOTES_TO_PLAY
        note_count = len(notes)
    else:
        notes = list(range(128))
        note_count = 128
    
    total_files = len(PRESETS) * note_count
    
    print(f"\nPresets: {len(PRESETS)}")
    print(f"Notes per preset: {note_count}")
    print(f"Total files: {total_files}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"\nFormat: {{PRESET}}_{{NOTE}}.wav")
    print("Example: ACORDEON_DE_SINALOA_C4.wav")
    
    midi_port = get_midi_output()
    if not midi_port:
        print("\nERROR: No MIDI output found!")
        return
    
    print(f"\nMIDI: {midi_port}")
    
    print("\n" + "=" * 60)
    print("SETUP:")
    print("1. FL Studio with BANDA CORRIDOS VST loaded")
    print("2. Audio Output = Virtual Audio Cable")
    print("3. MIDI Input = loopMIDI port")
    print("4. VST should respond to Program Changes")
    print("5. Press ENTER to start...")
    print("=" * 60 + "\n")
    
    input("Press ENTER to start...")
    
    # Iterate through presets
    for preset_idx, preset_name in enumerate(PRESETS):
        print(f"\n{'='*60}")
        print(f"[{preset_idx+1}/{len(PRESETS)}] Preset: {preset_name}")
        print("=" * 60)
        
        # Send program change (VST should switch to this preset)
        print(f"  Switching to preset {preset_idx}...")
        send_program_change(midi_port, preset_idx, MIDI_CHANNEL)
        time.sleep(0.3)  # Wait for preset to load
        
        preset_dir = os.path.join(OUTPUT_DIR, safe_filename(preset_name))
        os.makedirs(preset_dir, exist_ok=True)
        
        # Play notes
        for note_idx, midi_note in enumerate(notes):
            note_name = midi_to_note_name(midi_note)
            filename = f"{safe_filename(preset_name)}_{note_name_to_filename(note_name)}.wav"
            output_path = os.path.join(preset_dir, filename)
            
            print(f"  [{note_idx+1}/{note_count}] {note_name}...", end=" ", flush=True)
            
            # Send note on
            send_note_on(midi_port, midi_note, NOTE_VELOCITY, MIDI_CHANNEL)
            
            # Record
            audio = record_audio(NOTE_DURATION + 0.1, SAMPLE_RATE, VAC_DEVICE)
            
            # Note off
            send_note_off(midi_port, midi_note, MIDI_CHANNEL)
            
            # Save only if not silent
            if not is_silent(audio, SILENCE_THRESHOLD):
                save_wav(output_path, audio)
                print("Saved")
            else:
                print("Silent - skipped")
            
            time.sleep(0.05)
    
    print("\n" + "=" * 60)
    print("DONE!")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
