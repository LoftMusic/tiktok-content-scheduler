"""
Magenta MelodyRNN - Full Pipeline v3
Cu Markov Order 2 și filtrare pe scală
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
import mido
import random
from pathlib import Path
from collections import defaultdict

# Setari
DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\MAGENTA"
CONFIG_NAME = "basic_rnn"
BPM = 100
KEY_ROOT = 57  # A3
SCALES = {
    'min': [0, 2, 3, 5, 7, 8, 10],      # natural minor
    'maj': [0, 2, 4, 5, 7, 9, 11],      # major
    'phyr': [0, 1, 3, 5, 7, 8, 10],     # phrygian
    'phyr_dom': [0, 1, 3, 5, 7, 8, 11], # phrygian dominant
    'dor': [0, 2, 3, 5, 7, 9, 10],      # dorian
    'locrian': [0, 1, 3, 6, 7, 8, 10],  # locrian
    'lydian': [0, 2, 4, 6, 7, 9, 11],   # lydian
}

def get_scale_notes(root, scale_type='min'):
    """Get available notes for a scale."""
    return [root + semitone for semitone in SCALES[scale_type]]

def fits_scale(note, scale_notes):
    """Check if note fits in scale."""
    return (note % 12) in [n % 12 for n in scale_notes]

def closest_scale_note(note, scale_notes):
    """Find closest note in scale."""
    best = min(scale_notes, key=lambda x: min(abs(note - x), abs(note - x - 12), abs(note - x + 12)))
    return best

def extract_melodies():
    """Extract melodies using MelodyExtractor."""
    import note_seq as ns
    from magenta.pipelines.melody_pipelines import MelodyExtractor
    
    print("[i] Extracting melodies...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} files")
    
    melodies = []
    
    for i, f in enumerate(files):
        try:
            ns_proto = ns.midi_file_to_note_sequence(str(f))
            
            if len(list(ns_proto.notes)) < 4:
                continue
            
            quantized = ns.quantize_note_sequence(ns_proto, 4)
            
            extractor = MelodyExtractor(min_bars=1, max_steps=512, min_unique_pitches=2, ignore_polyphonic_notes=True)
            result = extractor.transform(quantized)
            
            if result and len(result) > 0:
                melody = result[0]
                melodies.append({
                    'melody': melody,
                    'events': list(melody._events),
                    'file': f.name
                })
                print(f"  [{i+1}] {f.name}: {len(melody._events)} events")
                
        except Exception as e:
            print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Extracted {len(melodies)} melodies")
    return melodies

def build_markov_chain(melodies, order=2):
    """Build Markov transition table with specified order."""
    transitions = defaultdict(list)
    
    for m in melodies:
        events = m['events']
        if len(events) <= order:
            continue
        
        for i in range(len(events) - order):
            state = tuple(events[i:i+order])
            next_event = events[i+order]
            transitions[state].append(next_event)
    
    return transitions

def generate_markov_v2(melodies, transitions, num_events=128, scale_notes=None, use_pattern_aabb=True):
    """Generate melody using Markov chain order 2."""
    sequence = []
    
    # Start with random state from first melody
    m = melodies[0]
    start_events = m['events'][:2]
    state = tuple(start_events)
    sequence.extend(start_events)
    
    for _ in range(num_events - len(sequence)):
        if state in transitions and len(transitions[state]) > 0:
            next_event = random.choice(transitions[state])
        else:
            # Fallback - random from any melody
            m = melodies[random.randint(0, len(melodies)-1)]
            next_event = random.choice(m['events'])
        
        # If scale filtering enabled, adjust note
        if scale_notes is not None:
            if next_event >= 0:
                # It's a note event, ensure it fits scale
                if not fits_scale(next_event, scale_notes):
                    next_event = closest_scale_note(next_event, scale_notes)
        
        sequence.append(next_event)
        state = tuple(sequence[-2:])
    
    # Pattern AABB - repeat first 64 events
    if use_pattern_aabb and len(sequence) >= 64:
        first_half = sequence[:64]
        sequence = first_half + first_half
    
    return sequence

def decode_events_to_midi(events, output_path, bpm=100):
    """Convert event list to MIDI file."""
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))
    
    tick_duration = 120  # 16th notes at 480 ticks/beat
    
    for event in events:
        if event >= 0:
            pitch = 48 + (event % 24)
            pitch = max(36, min(84, pitch))
            
            track.append(mido.Message('note_on', note=pitch, velocity=90, time=0))
            track.append(mido.Message('note_off', note=pitch, velocity=64, time=tick_duration))
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def main():
    print("=" * 60)
    print("Magenta MelodyRNN Pipeline v3")
    print("=" * 60)
    
    # Extract melodies
    print("\n[1] Extracting melodies...")
    melodies = extract_melodies()
    
    if not melodies:
        print("[!] No melodies extracted!")
        return
    
    print(f"\n[OK] Extracted {len(melodies)} melodies")
    
    # Build Markov chain (order 2)
    print("\n[2] Building Markov chain (order 2)...")
    transitions = build_markov_chain(melodies, order=2)
    print(f"[OK] {len(transitions)} unique states")
    
    # Generate multiple variations
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n[3] Generating variations...")
    
    # Generate with and without scale filtering
    scale_notes = get_scale_notes(57, 'min')  # A minor
    
    for var in range(1, 4):
        print(f"\n  Variation {var}:")
        
        # Generate with AABB pattern
        generated = generate_markov_v2(
            melodies, 
            transitions, 
            num_events=128, 
            scale_notes=scale_notes,
            use_pattern_aabb=True
        )
        
        output_file = os.path.join(OUTPUT_DIR, f"ritornela_Amin_{BPM}bpm_v{var}.mid")
        decode_events_to_midi(generated, output_file, bpm=BPM)
        print(f"  [OK] Saved: {output_file}")
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()