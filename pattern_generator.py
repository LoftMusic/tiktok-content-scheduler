"""
Pattern-based MIDI Generator - Guitar Edition
Generates guitar patterns from MIDI dataset
"""

import os
import sys
import mido
from pathlib import Path
from collections import defaultdict
import random

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATASET_DIR = r"G:\Modele AI\New folder"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED_GUITAR"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Progresie de acorduri (A minor key)
CHORDS = {
    'i': {'name': 'Amin', 'notes': [57, 60, 64]},  # A, C, E
    'IV': {'name': 'Fmaj', 'notes': [53, 57, 60]}, # F, A, C
    'V': {'name': 'Gmaj', 'notes': [55, 59, 62]},  # G, B, D
    'III': {'name': 'Cmaj', 'notes': [60, 64, 67]},# C, E, G
}

PROGRESSION = ['i', 'IV', 'III', 'V']  # Amin → Fmaj → Cmaj → Gmaj
CHORD_MEASURES = 2  # Masuri per acord

def extract_note_events(midi_path):
    """Extract note events with durations."""
    mid = mido.MidiFile(midi_path)
    events = []
    
    ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
    
    for track in mid.tracks:
        current_time = 0
        notes_on = {}
        
        for msg in track:
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_on[msg.note] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in notes_on:
                    start = notes_on[msg.note]
                    end = current_time
                    duration = end - start
                    
                    duration_16th = max(1, int(duration / (ticks_per_beat / 4)))
                    
                    events.append({
                        'pitch': msg.note,
                        'duration': duration_16th,
                        'start': start / ticks_per_beat
                    })
                    
                    del notes_on[msg.note]
    
    return events

def extract_patterns(all_events, min_length=3):
    """Extract repeated patterns from dataset."""
    note_patterns = defaultdict(list)
    
    for events in all_events:
        for i in range(len(events) - min_length):
            pattern_notes = tuple(e['pitch'] for e in events[i:i+min_length])
            pattern_durations = tuple(e['duration'] for e in events[i:i+min_length])
            
            note_patterns[pattern_notes].append(pattern_durations)
    
    return note_patterns

def extract_melody_stats(all_events):
    """Extract statistics about melodies."""
    stats = {
        'avg_duration': [],
        'transitions': defaultdict(lambda: defaultdict(int)),
    }
    
    for events in all_events:
        if len(events) < 2:
            continue
        
        durations = [e['duration'] for e in events]
        stats['avg_duration'].append(sum(durations) / len(durations))
        
        for i in range(len(events) - 1):
            current = events[i]
            next_note = events[i + 1]
            stats['transitions'][current['pitch']][next_note['pitch']] += 1
    
    return stats

def get_chord_notes(chord_name):
    """Get notes for a chord."""
    return CHORDS.get(chord_name, CHORDS['i'])['notes']

def get_chord_for_measure(measure_idx):
    """Get chord for a given measure (0-indexed)."""
    measures_per_chord = CHORD_MEASURES
    chord_idx = (measure_idx // measures_per_chord) % len(PROGRESSION)
    return PROGRESSION[chord_idx]

def fits_chord(pitch, chord_notes):
    """Check if pitch fits in chord."""
    return any(abs(pitch - cn) % 12 == 0 for cn in chord_notes)

def closest_chord_note(pitch, chord_notes):
    """Find closest pitch in chord."""
    best = min(chord_notes, key=lambda x: min(
        abs(pitch - x), 
        abs(pitch - x - 12), 
        abs(pitch - x + 12)
    ))
    return best

def generate_melody_with_chords(patterns, stats, num_measures=8, num_variations=3):
    """Generate melody using extracted patterns with chord constraints."""
    
    target_notes = num_measures * 16  # 16th notes per measure
    
    for var in range(num_variations):
        melody = []
        
        for measure in range(num_measures):
            # Get chord for this measure
            chord_name = get_chord_for_measure(measure)
            chord_notes = get_chord_notes(chord_name)
            
            measures_per_chord = CHORD_MEASURES
            notes_in_this_chord = measures_per_chord * 16
            
            # Generate notes for this chord section
            start_idx = len(melody)
            end_idx = min(start_idx + notes_in_this_chord, target_notes)
            
            # Start with a chord note
            if not melody:
                # First note - start with root of first chord
                melody.append({
                    'pitch': chord_notes[0],
                    'duration': random.choice([4, 8, 16])
                })
            else:
                # Use last note, adjust to chord if needed
                last_pitch = melody[-1]['pitch']
                if not fits_chord(last_pitch, chord_notes):
                    melody.append({
                        'pitch': closest_chord_note(last_pitch, chord_notes),
                        'duration': random.choice([4, 8, 16])
                    })
            
            # Continue using patterns, prioritizing chord notes
            while len(melody) < end_idx:
                last_pitch = melody[-1]['pitch']
                
                # Try to find a pattern starting with this note
                matching_patterns = []
                for pattern in patterns.keys():
                    if pattern[0] == last_pitch:
                        matching_patterns.append(pattern)
                
                if matching_patterns:
                    selected = random.choice(matching_patterns)
                    for pitch in selected[1:]:
                        # Ensure chord note
                        if not fits_chord(pitch, chord_notes):
                            pitch = closest_chord_note(pitch, chord_notes)
                        melody.append({'pitch': pitch, 'duration': random.choice([4, 8, 16])})
                else:
                    # Fallback - Markov-style
                    if last_pitch in stats['transitions']:
                        next_notes = stats['transitions'][last_pitch]
                        next_pitch = max(next_notes, key=next_notes.get)
                        if not fits_chord(next_pitch, chord_notes):
                            next_pitch = closest_chord_note(next_pitch, chord_notes)
                        melody.append({'pitch': next_pitch, 'duration': random.choice([4, 8, 16])})
                    else:
                        melody.append({
                            'pitch': random.choice(chord_notes),
                            'duration': random.choice([4, 8, 16])
                        })
            
            # Truncate if needed
            melody = melody[:end_idx]
        
        # Truncate to target
        melody = melody[:target_notes]
        
        # Ensure AABB pattern (repeat first half)
        if len(melody) >= 16:
            half = len(melody) // 2
            first_half = melody[:half]
            melody = first_half + first_half
        
        # Save MIDI
        save_midi_with_chord_labels(melody, OUTPUT_DIR, var + 1, PROGRESSION, CHORD_MEASURES)
        
        print(f"  [{var+1}] Generated {len(melody)} notes")

def save_midi_with_chord_labels(events, output_dir, variation, progression, measures_per_chord):
    """Save events to MIDI file with chord info in comments."""
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(100)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))  # Sax
    
    current_tick = 0
    for event in events:
        pitch = max(36, min(84, event['pitch']))
        duration_ticks = event['duration'] * 30
        
        track.append(mido.Message('note_on', note=pitch, velocity=90, time=0))
        track.append(mido.Message('note_off', note=pitch, velocity=64, time=duration_ticks))
    
    track.append(mido.MetaMessage('end_of_track'))
    
    # Add chord labels as text events
    current_measure = 0
    for i, chord_name in enumerate(progression):
        chord_info = CHORDS[chord_name]
        measure_start = current_measure * 16 * 30  # ticks
        track.insert(1, mido.MetaMessage('text', time=measure_start, text=f"Chord: {chord_info['name']}"))
        current_measure += measures_per_chord
    
    output_file = os.path.join(output_dir, f"ritornela_chord_{variation}.mid")
    mid.save(output_file)
    print(f"  Saved: {output_file}")

def main():
    print("=" * 60)
    print("Pattern-based MIDI Generator (with Chords)")
    print("=" * 60)
    
    print(f"\nProgresie: {' > '.join([CHORDS[c]['name'] for c in PROGRESSION])}")
    print(f"Masuri per acord: {CHORD_MEASURES}")
    
    # Extract events
    print("\n[1] Analyzing dataset...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} MIDI files")
    
    all_events = []
    
    for i, f in enumerate(files):
        try:
            events = extract_note_events(str(f))
            if events:
                all_events.append(events)
                print(f"  [{i+1}] {f.name}: {len(events)} notes")
        except Exception as e:
            print(f"  [ERROR] {f.name}: {str(e)[:50]}")
    
    print(f"\n[OK] Loaded {len(all_events)} melodies")
    
    # Extract patterns
    print("\n[2] Extracting patterns...")
    patterns = extract_patterns(all_events, min_length=3)
    print(f"[OK] Found {len(patterns)} unique patterns")
    
    # Extract statistics
    print("\n[3] Extracting statistics...")
    stats = extract_melody_stats(all_events)
    print(f"[OK] Avg duration: {sum(stats['avg_duration'])/len(stats['avg_duration']):.1f} 16ths")
    
    # Generate
    print(f"\n[4] Generating melodies...")
    
    generate_melody_with_chords(patterns, stats, num_measures=8, num_variations=3)
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()