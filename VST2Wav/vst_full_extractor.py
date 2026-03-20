"""
VST Full Range Extractor
Plays ALL MIDI notes (C-1 to G8) and records each one
Automatically removes silent/empty notes
"""

import sounddevice as sd
import numpy as np
import os
import time
from scipy.io import wavfile
import mido
from mido import Message
import shutil

# Configuration
OUTPUT_DIR = r"C:\Samples\BANDA_CORRIDOS_NOTES"
VAC_DEVICE = 1  # Virtual Audio Cable
SAMPLE_RATE = 44100
NOTE_DURATION = 0.5  # seconds per note
NOTE_VELOCITY = 100
SILENCE_THRESHOLD = 0.01  # Notes quieter than this will be deleted

# MIDI note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Keep track of notes for deletion list
recorded_notes = []

def midi_to_note_name(midi_num):
    """Convert MIDI number to note name (C-1 to G8)"""
    octave = (midi_num // 12) - 1
    note = NOTE_NAMES[midi_num % 12]
    return f"{note}{octave}"

def note_name_to_filename(note_name):
    """Convert note name to safe filename"""
    return note_name.replace('#', 's')

def get_midi_output():
    """Find available MIDI output ports"""
    ports = mido.get_output_names()
    
    # Look for loopMIDI or similar virtual port
    for port in ports:
        if 'loop' in port.lower() or 'touch' in port.lower() or 'python' in port.lower():
            return port
    
    # Return first available
    if ports:
        return ports[0]
    return None

def send_midi_note(port, note, velocity, duration):
    """Send Note On, wait, Note Off"""
    if port:
        try:
            with mido.open_output(port) as midi_out:
                midi_out.send(Message('note_on', note=note, velocity=velocity))
                time.sleep(duration)
                midi_out.send(Message('note_off', note=note, velocity=0))
        except Exception as e:
            print(f"MIDI Error: {e}")

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
    """Check if audio is silent (below threshold)"""
    # Combine channels and get max amplitude
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    max_amp = np.max(np.abs(audio))
    return max_amp < threshold

def save_wav(filename, audio):
    """Save audio to WAV file"""
    max_val = np.max(np.abs(audio))
    if max_val > 0.01:
        audio = audio / max_val * 0.9
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filename, SAMPLE_RATE, audio_int16)

def delete_silent_notes(output_dir, threshold=0.01):
    """Delete WAV files that are below the silence threshold"""
    deleted_count = 0
    kept_count = 0
    
    print("\n" + "=" * 60)
    print("Cleaning up silent notes...")
    print("=" * 60)
    
    for filename in os.listdir(output_dir):
        if filename.endswith('.wav'):
            filepath = os.path.join(output_dir, filename)
            
            try:
                # Read WAV
                sr, audio = wavfile.read(filepath)
                
                # Convert to float for analysis
                audio_float = audio.astype(np.float32) / 32767.0
                
                if is_silent(audio_float, threshold):
                    os.remove(filepath)
                    print(f"  Deleted (silent): {filename}")
                    deleted_count += 1
                else:
                    kept_count += 1
            except Exception as e:
                print(f"  Error checking {filename}: {e}")
    
    print(f"\n  Kept: {kept_count} notes")
    print(f"  Deleted: {deleted_count} silent notes")
    return deleted_count, kept_count

def main():
    print("=" * 60)
    print("VST Full Range Extractor")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"Device: Virtual Audio Cable (#{VAC_DEVICE})")
    print(f"Notes: C-1 to G8 (128 notes)")
    print(f"Duration: {NOTE_DURATION}s per note")
    print(f"Silence threshold: {SILENCE_THRESHOLD}")
    
    # Check MIDI
    midi_port = get_midi_output()
    if midi_port:
        print(f"\nMIDI Output: {midi_port}")
    else:
        print("\nWARNING: No MIDI output found!")
        print("Install loopMIDI and create a virtual port")
        print("Download: https://www.tobias-erichsen.de/software/loopmidi.html")
        return
    
    # Check audio device
    try:
        dev_info = sd.query_devices(VAC_DEVICE)
        print(f"Audio Input: {dev_info['name']}")
    except:
        print(f"\nERROR: Device {VAC_DEVICE} not found!")
        print("Available input devices:")
        for i in range(sd.device_count()):
            d = sd.query_devices(i)
            if d['max_input_channels'] > 0:
                print(f"  {i}: {d['name']}")
        return
    
    print("\n" + "=" * 60)
    print("SETUP:")
    print("1. loopMIDI running with a virtual port")
    print("2. FL Studio (or any DAW):")
    print("   - Load BANDA CORRIDOS VST")
    print("   - Audio Output = Virtual Audio Cable")
    print("   - MIDI Input = loopMIDI port")
    print("3. VST should be ready to play")
    print("4. Press ENTER to start...")
    print("=" * 60 + "\n")
    
    input("Press ENTER to start recording...")
    
    # Record all 128 notes
    print("\nRecording all 128 MIDI notes...\n")
    
    for midi_note in range(128):
        note_name = midi_to_note_name(midi_note)
        filename = note_name_to_filename(note_name)
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.wav")
        
        print(f"[{midi_note:3d}/127] {note_name:4s}...", end=" ", flush=True)
        
        # Send MIDI note
        send_midi_note(midi_port, midi_note, NOTE_VELOCITY, NOTE_DURATION)
        
        # Record audio
        audio = record_audio(NOTE_DURATION + 0.1, SAMPLE_RATE, VAC_DEVICE)
        
        # Save
        save_wav(output_path, audio)
        
        # Track
        recorded_notes.append((note_name, output_path))
        
        print("Saved")
        
        # Small gap between notes
        time.sleep(0.05)
    
    # Clean up silent notes
    deleted, kept = delete_silent_notes(OUTPUT_DIR, SILENCE_THRESHOLD)
    
    print("\n" + "=" * 60)
    print("DONE!")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Total notes: {kept} kept, {deleted} removed")
    print("=" * 60)

if __name__ == "__main__":
    main()
