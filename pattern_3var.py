"""
Pattern Generator - 3 Variations per Setting
"""

import os
import mido
from pathlib import Path
from collections import defaultdict
import random

DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_measures(midi_path):
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
    patterns = defaultdict(list)
    for i in range(len(notes) - 1):
        pattern = notes[i]['pitch']
        next_note = (notes[i+1]['pitch'], notes[i+1]['duration'])
        patterns[pattern].append(next_note)
    return patterns

def get_scale_pitches(root, scale='minor'):
    scales = {
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'major': [0, 2, 4, 5, 7, 9, 11],
    }
    return [root + s for s in scales.get(scale, scales['minor'])]

def save_midi_from_notes(notes, output_path, bpm=100):
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))
    
    ticks_per_beat = 480
    ticks_per_note = ticks_per_beat // 4
    
    current_tick = 0
    for note in notes:
        pitch = note['pitch']
        dur_ticks = note['duration'] * ticks_per_note
        
        track.append(mido.Message('note_on', note=pitch, velocity=90, time=current_tick))
        track.append(mido.Message('note_off', note=pitch, velocity=64, time=dur_ticks))
        
        current_tick = 0
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def main():
    print("=" * 60)
    print("Pattern Generator - 3 Variations")
    print("=" * 60)
    
    # Load dataset
    print("\n[1] Loading dataset...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    all_notes = []
    
    for f in files:
        try:
            notes = extract_measures(str(f))
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
        ('Amin', 57, 'minor', 126),
        ('Amin', 57, 'minor', 100),
        ('Emin', 52, 'minor', 126),
        ('Dmin', 50, 'minor', 126),
        ('Fmin', 53, 'minor', 100),
    ]
    
    count = 0
    for name, key_root, scale_name, bpm in settings:
        scale = get_scale_pitches(key_root, scale_name)
        
        # Generate 3 variations
        for v in range(1, 4):
            # Start with random scale note
            melody = [{'pitch': random.choice(scale), 'duration': random.choice([4, 8, 16])}]
            
            # Continue using patterns
            for _ in range(127):
                last_pitch = melody[-1]['pitch']
                
                if last_pitch in patterns:
                    next_entry = random.choice(patterns[last_pitch])
                    next_pitch = next_entry[0]
                    next_dur = next_entry[1]
                else:
                    next_pitch = random.choice(scale)
                    next_dur = random.choice([4, 8, 16])
                
                melody.append({'pitch': next_pitch, 'duration': next_dur})
            
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