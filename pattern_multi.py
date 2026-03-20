"""
Pattern-based Generator - Variatii multiple
"""

import os
import mido
from pathlib import Path
from collections import defaultdict
import random

DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_measures(midi_path, steps_per_measure=16):
    """Extract measures from MIDI."""
    mid = mido.MidiFile(midi_path)
    measures = []
    
    ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
    ticks_per_measure = ticks_per_beat * 4
    
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
                    
                    measures.append({
                        'pitch': msg.note,
                        'duration': note_duration,
                        'start': 0
                    })
                    
                    del notes_on[msg.note]
    
    return measures

def extract_patterns(measures):
    """Extract measure patterns."""
    patterns = defaultdict(list)
    
    for m in measures:
        pattern = tuple((e['pitch'], e['duration']) for e in m)
        patterns[pattern].append(m)
    
    return patterns

def get_scale_pitches(root, scale='minor'):
    scales = {
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'major': [0, 2, 4, 5, 7, 9, 11],
    }
    return [root + s for s in scales.get(scale, scales['minor'])]

def save_midi_from_measures(measures, output_path, bpm=100):
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))
    
    ticks_per_beat = 480
    measure_start = 0
    ticks_per_measure = ticks_per_beat * 4
    
    for measure in measures:
        current_tick = measure_start
        for note in measure:
            pitch = note['pitch']
            dur_tick = int(note['duration'] * (ticks_per_beat / 4))
            
            track.append(mido.Message('note_on', note=pitch, velocity=90, time=current_tick))
            track.append(mido.Message('note_off', note=pitch, velocity=64, time=dur_tick))
            current_tick = 0
        
        measure_start += ticks_per_measure
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def main():
    print("=" * 60)
    print("Pattern Generator - Multiple Variations")
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
    
    # Build patterns from consecutive notes
    print("\n[2] Building patterns...")
    patterns = defaultdict(list)
    for i in range(len(all_notes) - 1):
        pattern = (all_notes[i]['pitch'], all_notes[i]['duration'])
        next_note = (all_notes[i+1]['pitch'], all_notes[i+1]['duration'])
        patterns[pattern].append(next_note)
    print(f"[OK] Found {len(patterns)} unique note patterns")
    
    # Generate variations
    print("\n[3] Generating variations...")
    
    keys = [
        ('Amin', 57, 'minor'),
        ('Emin', 52, 'minor'),
        ('Dmin', 50, 'minor'),
        ('Fmin', 53, 'minor'),
        ('Cmaj', 60, 'major'),
    ]
    
    bpms = [100, 120, 126]
    num_variations = 2  # 2 var per setting
    
    count = 0
    for key_name, key_root, scale_name in keys:
        scale = get_scale_pitches(key_root, scale_name)
        
        for bpm in bpms:
            for v in range(1, num_variations + 1):
                # Start with random note
                melody = [{'pitch': random.choice(scale), 'duration': random.choice([4, 8, 16])}]
                
                # Continue using patterns
                for _ in range(127):  # 128 notes total
                    if patterns:
                        last = (melody[-1]['pitch'], melody[-1]['duration'])
                        if last in patterns:
                            next_note = random.choice(patterns[last])
                        else:
                            next_note = (random.choice(scale), random.choice([4, 8, 16]))
                    else:
                        next_note = (random.choice(scale), random.choice([4, 8, 16]))
                    
                    melody.append({'pitch': next_note[0], 'duration': next_note[1]})
                
                # Convert to measures for save
                melody_measures = []
                for i in range(0, len(melody), 16):
                    melody_measures.append(melody[i:i+16])
                
                output_path = os.path.join(OUTPUT_DIR, f"pattern_{key_name}_{bpm}bpm_v{v}.mid")
                save_midi_from_measures(melody_measures, output_path, bpm=bpm)
                
                print(f"  [{key_name}][{bpm}bpm][v{v}] Saved: {output_path}")
                count += 1
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Generated {count} files!")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()