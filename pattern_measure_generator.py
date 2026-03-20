"""
Pattern-based Generator cu Structură Muzicală
Extrage blocuri (măsuri) reale și le recombină
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
    ticks_per_measure = ticks_per_beat * 4  # 4/4 time
    
    current_measure = []
    current_tick = 0
    
    for track in mid.tracks:
        notes_on = {}
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_on[msg.note] = current_tick
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in notes_on:
                    start = notes_on[msg.note]
                    
                    # Convert to measure-relative
                    measure_num = start // ticks_per_measure
                    note_start = start % ticks_per_measure
                    
                    duration = current_tick - start
                    note_duration = int(duration / (ticks_per_beat / 4))
                    
                    current_measure.append({
                        'pitch': msg.note,
                        'start': note_start,
                        'duration': note_duration
                    })
                    
                    # Check if we finished a measure
                    if current_tick >= (measure_num + 1) * ticks_per_measure:
                        if current_measure:
                            measures.append(current_measure)
                        current_measure = []
                    
                    del notes_on[msg.note]
    
    # Add last measure
    if current_measure:
        measures.append(current_measure)
    
    return measures

def extract_patterns(measures):
    """Extract measure patterns."""
    patterns = defaultdict(list)
    
    for m in measures:
        # Create pattern from this measure
        pattern = tuple((e['pitch'], e['duration']) for e in m)
        patterns[pattern].append(m)
    
    return patterns

def get_scale_pitches(root, scale='minor'):
    """Get scale notes."""
    scales = {
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'major': [0, 2, 4, 5, 7, 9, 11],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
    }
    return [root + s for s in scales.get(scale, scales['minor'])]

def fits_scale(pitch, scale):
    return (pitch % 12) in [s % 12 for s in scale]

def closest_scale_pitch(pitch, scale):
    return min(scale, key=lambda x: min(abs(pitch - x), abs(pitch - x - 12), abs(pitch - x + 12)))

def save_midi_from_measures(measures, output_path, bpm=100):
    """Save measures as MIDI."""
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))
    
    ticks_per_beat = 480
    ticks_per_measure = ticks_per_beat * 4  # 4/4 time
    
    measure_start = 0
    for measure in measures:
        current_tick = measure_start
        
        for note in measure:
            pitch = note['pitch']
            # Note start is relative to measure start
            start_tick = current_tick
            dur_tick = int(note['duration'] * (ticks_per_beat / 4))
            
            track.append(mido.Message('note_on', note=pitch, velocity=90, time=start_tick))
            track.append(mido.Message('note_off', note=pitch, velocity=64, time=dur_tick))
            
            current_tick = 0  # Reset tick for next note in same measure
        
        measure_start += ticks_per_measure
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def main():
    print("=" * 60)
    print("Pattern-based MIDI Generator (Measure-level)")
    print("=" * 60)
    
    # Extract measures
    print("\n[1] Extracting measures...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} files")
    
    all_measures = []
    
    for f in files:
        try:
            measures = extract_measures(str(f))
            all_measures.extend(measures)
            print(f"  {f.name}: {len(measures)} measures")
        except Exception as e:
            print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Total measures: {len(all_measures)}")
    
    # Extract patterns
    print("\n[2] Extracting patterns...")
    patterns = extract_patterns(all_measures)
    print(f"[OK] Found {len(patterns)} unique measure patterns")
    
    # Generate
    print("\n[3] Generating melodies...")
    
    scale_Amin = get_scale_pitches(57, 'minor')  # A3
    scale_Emin = get_scale_pitches(52, 'minor')  # E3
    
    # Generate A minor, 126 BPM
    print("\n  Generating A minor, 126 BPM...")
    melody_measures = []
    for i in range(8):  # 8 measures
        if patterns:
            pattern = random.choice(list(patterns.keys()))
            measure = list(random.choice(patterns[pattern]))
        else:
            measure = []
            for _ in range(16):
                note = random.choice(scale_Amin)
                measure.append({'pitch': note, 'duration': random.choice([4, 8, 16]), 'start': 0})
        melody_measures.append(measure)
    
    output_path = os.path.join(OUTPUT_DIR, "pattern_Amin_126bpm.mid")
    save_midi_from_measures(melody_measures, output_path, bpm=126)
    print(f"    Saved: {output_path}")
    
    # Generate A minor, 100 BPM
    print("\n  Generating A minor, 100 BPM...")
    melody_measures = []
    for i in range(8):
        if patterns:
            pattern = random.choice(list(patterns.keys()))
            measure = list(random.choice(patterns[pattern]))
        else:
            measure = []
            for _ in range(16):
                note = random.choice(scale_Amin)
                measure.append({'pitch': note, 'duration': random.choice([4, 8, 16]), 'start': 0})
        melody_measures.append(measure)
    
    output_path = os.path.join(OUTPUT_DIR, "pattern_Amin_100bpm.mid")
    save_midi_from_measures(melody_measures, output_path, bpm=100)
    print(f"    Saved: {output_path}")
    
    # Generate E minor, 126 BPM
    print("\n  Generating E minor, 126 BPM...")
    melody_measures = []
    for i in range(8):
        if patterns:
            pattern = random.choice(list(patterns.keys()))
            measure = list(random.choice(patterns[pattern]))
        else:
            measure = []
            for _ in range(16):
                note = random.choice(scale_Emin)
                measure.append({'pitch': note, 'duration': random.choice([4, 8, 16]), 'start': 0})
        melody_measures.append(measure)
    
    output_path = os.path.join(OUTPUT_DIR, "pattern_Emin_126bpm.mid")
    save_midi_from_measures(melody_measures, output_path, bpm=126)
    print(f"    Saved: {output_path}")
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()