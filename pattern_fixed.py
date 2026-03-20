"""
Pattern-based Generator - Corrected
Folosește scale și BPM corect
"""

import os
import mido
from pathlib import Path
from collections import defaultdict
import random

DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Scale configuration
SCALES = {
    'Amin': {'root': 57, 'notes': [0, 2, 3, 5, 7, 8, 10]},  # A minor
    'Emin': {'root': 52, 'notes': [0, 2, 3, 5, 7, 8, 10]},  # E minor
    'Dmin': {'root': 50, 'notes': [0, 2, 3, 5, 7, 8, 10]},  # D minor
    'Fmin': {'root': 53, 'notes': [0, 2, 3, 5, 7, 8, 10]},  # F minor
    'Cmaj': {'root': 60, 'notes': [0, 2, 4, 5, 7, 9, 11]},   # C major
}

def extract_notes_from_midi(midi_path):
    """Extract all notes from MIDI."""
    mid = mido.MidiFile(midi_path)
    notes = []
    
    ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
    
    for track in mid.tracks:
        notes_on = {}
        current_tick = 0
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_on[msg.note] = current_tick
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in notes_on:
                    start = notes_on[msg.note]
                    duration = current_tick - start
                    note_duration = int(duration / (ticks_per_beat / 4))
                    
                    notes.append({
                        'pitch': msg.note,
                        'duration': max(1, note_duration),
                        'start': 0
                    })
                    
                    del notes_on[msg.note]
    
    return notes

def build_patterns(notes):
    """Build note-to-note transition patterns."""
    patterns = defaultdict(list)
    for i in range(len(notes) - 1):
        pattern = notes[i]['pitch']
        next_note = (notes[i+1]['pitch'], notes[i+1]['duration'])
        patterns[pattern].append(next_note)
    return patterns

def fits_scale(pitch, scale_config):
    """Check if pitch is in scale."""
    root = scale_config['root']
    scale_notes = scale_config['notes']
    return (pitch - root) % 12 in scale_notes

def closest_scale_note(pitch, scale_config):
    """Find closest note in scale."""
    root = scale_config['root']
    scale_notes = scale_config['notes']
    
    best = min(scale_notes, key=lambda s: min(
        abs(pitch - (root + s)),
        abs(pitch - (root + s - 12)),
        abs(pitch - (root + s + 12))
    ))
    return root + best

def save_midi_from_notes(notes, output_path, bpm=100):
    """Save notes as MIDI with correct BPM."""
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set correct tempo
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))
    
    # Notes per beat = 4 (16th notes)
    ticks_per_beat = 480
    ticks_per_note = ticks_per_beat // 4
    
    current_tick = 0
    for note in notes:
        pitch = note['pitch']
        dur_ticks = note['duration'] * ticks_per_note
        
        track.append(mido.Message('note_on', note=pitch, velocity=90, time=current_tick))
        track.append(mido.Message('note_off', note=pitch, velocity=64, time=dur_ticks))
        
        current_tick = 0  # Reset for next note
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def generate_melody(patterns, scale_config, length=128):
    """Generate melody using patterns with scale constraints."""
    root = scale_config['root']
    scale_notes = scale_config['notes']
    
    # Start with a random scale note
    start_note = random.choice(scale_notes) + root
    melody = [{'pitch': start_note, 'duration': random.choice([4, 8, 16])}]
    
    # Continue using patterns
    for _ in range(length - 1):
        last_pitch = melody[-1]['pitch']
        
        if last_pitch in patterns:
            next_entry = random.choice(patterns[last_pitch])
            next_pitch = next_entry[0]
            next_dur = next_entry[1]
            
            # Force to scale
            if not fits_scale(next_pitch, scale_config):
                next_pitch = closest_scale_note(next_pitch, scale_config)
            
            melody.append({
                'pitch': next_pitch,
                'duration': next_dur
            })
        else:
            # Fallback: random scale note
            next_pitch = random.choice(scale_notes) + root
            melody.append({
                'pitch': next_pitch,
                'duration': random.choice([4, 8, 16])
            })
    
    return melody

def main():
    print("=" * 60)
    print("Pattern Generator - Corrected")
    print("=" * 60)
    
    # Load dataset
    print("\n[1] Loading dataset...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    all_notes = []
    
    for f in files:
        try:
            notes = extract_notes_from_midi(str(f))
            all_notes.extend(notes)
            print(f"  {f.name}: {len(notes)} notes")
        except Exception as e:
            print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Total notes: {len(all_notes)}")
    
    # Build patterns
    print("\n[2] Building patterns...")
    patterns = build_patterns(all_notes)
    print(f"[OK] Found {len(patterns)} unique patterns")
    
    # Generate variations
    print("\n[3] Generating variations...")
    
    settings = [
        ('Amin', 'Amin', 126),
        ('Amin', 'Amin', 100),
        ('Emin', 'Emin', 126),
        ('Amin', 'Amin', 85),
    ]
    
    count = 0
    for name, key, bpm in settings:
        scale_config = SCALES[key]
        
        # Generate 2 variations per setting
        for v in range(1, 3):
            melody = generate_melody(patterns, scale_config, length=128)
            
            output_path = os.path.join(OUTPUT_DIR, f"pattern_{name}_{bpm}bpm_v{v}.mid")
            save_midi_from_notes(melody, output_path, bpm=bpm)
            
            print(f"  [{name}][{bpm}bpm][v{v}] Saved: {output_path}")
            count += 1
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Generated {count} files!")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()