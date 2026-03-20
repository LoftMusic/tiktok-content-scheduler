"""
Magenta MelodyRNN - Full Pipeline v2
Folosește MelodyExtractor care a funcționat în test
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
import mido
import random
from pathlib import Path

# Setari
DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\MAGENTA"
CONFIG_NAME = "basic_rnn"
BPM = 100

def extract_melodies_melody_extractor():
    """Extract melodies using MelodyExtractor."""
    import note_seq as ns
    from magenta.pipelines.melody_pipelines import MelodyExtractor
    
    print("[i] Extracting melodies...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} files")
    
    melodies = []
    
    for i, f in enumerate(files):
        try:
            # Convert MIDI to NoteSequence
            ns_proto = ns.midi_file_to_note_sequence(str(f))
            
            if len(list(ns_proto.notes)) < 4:
                continue
            
            # Quantize
            quantized = ns.quantize_note_sequence(ns_proto, 4)
            
            # Extract melody
            extractor = MelodyExtractor(min_bars=1, max_steps=512, min_unique_pitches=2, ignore_polyphonic_notes=True)
            result = extractor.transform(quantized)
            
            if result and len(result) > 0:
                melody = result[0]
                melodies.append(melody)
                print(f"  [{i+1}] {f.name}: {len(list(ns_proto.notes))} notes -> melody extracted")
            else:
                print(f"  [!] {f.name}: no melody extracted")
                
        except Exception as e:
            print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Extracted {len(melodies)} melodies")
    return melodies

def encode_melody_to_events(melody):
    """Convert melody object to event list."""
    # Melody are _events attribute
    return list(melody._events)

def decode_events_to_midi(events, output_path, bpm=100):
    """Convert event list to MIDI file."""
    import mido
    
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    
    # Program change - saxophone
    track.append(mido.Message('program_change', program=65, channel=0))
    
    # Decode events
    # -2 = no event, -1 = note-off, 0-127 = note-on
    
    tick_duration = 120  # 16th notes
    
    for event in events:
        if event >= 0:
            # Note event - map to pitch (offset from C3)
            pitch = 48 + (event % 24)
            pitch = max(36, min(84, pitch))
            
            track.append(mido.Message('note_on', note=pitch, velocity=90, time=0))
            track.append(mido.Message('note_off', note=pitch, velocity=64, time=tick_duration))
        # else: -1 or -2 = rest/no event, do nothing (time accumulates)
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def generate_markov(melodies, num_events=128):
    """Generate melody using Markov chain on events."""
    from collections import defaultdict
    
    # Build transitions
    transitions = defaultdict(list)
    
    for melody in melodies:
        events = list(melody._events)
        for i in range(len(events) - 1):
            transitions[events[i]].append(events[i + 1])
    
    # Generate
    sequence = []
    
    # Start with random event from first melody
    start = melodies[0]._events[0]
    sequence.append(start)
    
    for _ in range(num_events - 1):
        current = sequence[-1]
        if current in transitions:
            next_event = random.choice(transitions[current])
            sequence.append(next_event)
        else:
            # Fallback - random from any melody
            m = melodies[random.randint(0, len(melodies)-1)]
            next_event = random.choice(list(m._events))
            sequence.append(next_event)
    
    return sequence

def main():
    print("=" * 60)
    print("Magenta MelodyRNN Pipeline v2")
    print("=" * 60)
    
    # Extract melodies
    print("\n[1] Extracting melodies from dataset...")
    melodies = extract_melodies_melody_extractor()
    
    if not melodies:
        print("[!] No melodies extracted!")
        return
    
    print(f"\n[OK] Extracted {len(melodies)} melodies")
    
    # Encode to events
    print("\n[2] Encoding melodies to events...")
    all_events = []
    for m in melodies:
        all_events.extend(encode_melody_to_events(m))
    print(f"[OK] Total events: {len(all_events)}")
    
    # Generate new melody
    print(f"\n[3] Generating new melody ({128} events)...")
    generated = generate_markov(melodies, num_events=128)
    
    # Save to MIDI
    output_file = os.path.join(OUTPUT_DIR, f"ritornela_magenta_{BPM}bpm_v1.mid")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n[4] Saving to {output_file}...")
    decode_events_to_midi(generated, output_file, bpm=BPM)
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done!")
    print(f"Output: {output_file}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()