"""MelodyRNN Training pentru Ritornele"""

import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import note_seq as ns
from magenta.models.melody_rnn import melody_rnn_model
from magenta.pipelines import melody_pipelines
import mido
from pathlib import Path

# Setari
DATASET_PATH = r"C:\midi_dataset"
OUTPUT_DIR = r"C:\midi_training"
CONFIG = "basic_rnn"

def midi_to_note_sequence(midi_path):
    """Converteste MIDI la note sequence."""
    mid = mido.MidiFile(midi_path)
    
    ns_proto = ns.NoteSequence()
    ticks_per_beat = mid.ticks_per_beat if hasattr(mid, 'ticks_per_beat') else 480
    ns_proto.ticks_per_quarter = ticks_per_beat
    
    current_time = 0
    notes_on = {}
    
    for track in mid.tracks:
        for msg in track:
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_on[msg.note] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in notes_on:
                    start_time = notes_on[msg.note]
                    end_time = current_time
                    
                    note = ns_proto.notes.add()
                    note.pitch = msg.note
                    note.start_time = start_time / ticks_per_beat
                    note.end_time = end_time / ticks_per_beat
                    note.velocity = msg.velocity if msg.type == 'note_on' else 64
                    
                    del notes_on[msg.note]
    
    return ns_proto

def create_training_data():
    """Creaza date de training din dataset."""
    print("[i] Scanning MIDI files...")
    
    files = list(Path(DATASET_PATH).glob("*.mid"))
    print(f"[i] Found {len(files)} files")
    
    sequences = []
    for i, f in enumerate(files):
        try:
            ns_proto = midi_to_note_sequence(str(f))
            if len(ns_proto.notes) > 0:
                sequences.append(ns_proto)
                print(f"  [{i+1}] {f.name}: {len(ns_proto.notes)} notes")
        except Exception as e:
            print(f"  [!] Error: {f.name}: {e}")
    
    print(f"\n[OK] Loaded {len(sequences)} sequences")
    return sequences

def main():
    print("=" * 50)
    print("MelodyRNN Training Setup")
    print("=" * 50)
    
    # Create output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create training data
    sequences = create_training_data()
    
    if not sequences:
        print("[!] No sequences loaded!")
        return
    
    # Get config
    config = melody_rnn_model.default_configs[CONFIG]
    print(f"\n[i] Config: {CONFIG}")
    print(f"[i] Steps per quarter: {config.steps_per_quarter}")
    
    # Quantize and encode melodies
    print("\n[>] Quantizing and encoding melodies...")
    
    encoded = []
    for ns_proto in sequences:
        try:
            # Quantize
            quantized = ns.quantize_note_sequence(ns_proto, config.steps_per_quarter)
            
            # Extract melody
            melody = ns.melody_encoder_decoder.encode(quantized)
            if melody and len(melody) > 4:
                encoded.append(melody)
        except Exception as e:
            pass  # Skip failed ones
    
    print(f"[OK] Encoded {len(encoded)} melodies")
    
    if len(encoded) < 5:
        print("[!] Not enough data for training!")
        print("\n[i] Alternativ: foloseste model pre-antrenat pentru generare")
        return
    
    # Save training info
    print(f"\n[OK] Dataset ready!")
    print(f"  - Sequences: {len(sequences)}")
    print(f"  - Encoded melodies: {len(encoded)}")
    print(f"  - Output: {OUTPUT_DIR}")
    print(f"\n[i] Acum poti antrena cu:")
    print(f"    melody_rnn_train --config={CONFIG} --run_dir={OUTPUT_DIR}")
    print(f"\n[i] SAU pot genera direct cu un model pre-antrenat!")

if __name__ == "__main__":
    main()