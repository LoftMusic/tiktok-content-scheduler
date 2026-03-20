"""
Markov Generator - SIMPLIFIED
"""

import os
import mido
import random
from collections import defaultdict
from pathlib import Path

DATASET_PATH = r"G:\MIDI PATTERNS\DATASET"
OUTPUT_PATH = r"G:\MIDI PATTERNS\GENERATED"

# Scale
SCALES = {
    'Emin': [0, 2, 3, 5, 7, 8, 10],
    'Dmin': [0, 2, 3, 5, 7, 8, 10],
    'BPhyr': [0, 1, 3, 5, 7, 8, 10],
}

def is_in_scale(note, scale, root=52):
    rel = (note - root) % 12
    return rel in scale

def quantize(note, scale, root=52):
    base = (note // 12) * 12
    rel = note % 12
    if rel in scale:
        return note
    # find closest
    closest = min(scale, key=lambda x: min(abs(x - rel), abs(x - rel + 12)))
    return base + closest

def main():
    # Settings
    BPM = 100
    SCALE = 'Emin'
    SCALE_ROOT = 52  # E3
    SCALE_NOTES = SCALES[SCALE]
    MEASURES = 8
    NOTES_PER_MEASURE = 16  # 4/4 * 4 sixteenths
    TOTAL_NOTES = MEASURES * NOTES_PER_MEASURE
    
    print(f"[i] BPM={BPM}, Scale={SCALE}, Measures={MEASURES}")
    
    # Load and analyze all MIDI files
    files = list(Path(DATASET_PATH).glob("*.mid"))
    print(f"[i] Loading {len(files)} files...")
    
    # Extract all notes as (pitch, duration) tuples
    all_notes = []
    for f in files:
        try:
            mid = mido.MidiFile(f)
            for track in mid.tracks:
                on_times = {}
                for msg in track:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        on_times[msg.note] = msg.time
                    elif msg.type == 'note_off' and msg.note in on_times:
                        dur = msg.time - on_times[msg.note]
                        del on_times[msg.note]
                        if dur >= 48:  # minimum duration
                            # Quantize to 16th (96 ticks)
                            d = max(1, dur // 96)
                            all_notes.append((msg.note, d))
        except:
            pass
    
    print(f"[OK] Extracted {len(all_notes)} notes")
    
    if len(all_notes) < 10:
        print("[!] Not enough notes!")
        return
    
    # Build bigram model: (note, dur) -> [(note, dur), ...]
    transitions = defaultdict(list)
    for i in range(len(all_notes) - 1):
        key = all_notes[i]
        val = all_notes[i + 1]
        transitions[key].append(val)
    
    print(f"[OK] {len(transitions)} unique states")
    
    # Generate
    print(f"\n[>] Generating {TOTAL_NOTES} notes...")
    
    # Start with a random note in scale
    valid_starts = [(n, d) for n, d in all_notes if is_in_scale(n, SCALE_NOTES, SCALE_ROOT)]
    if not valid_starts:
        valid_starts = all_notes[:10]
    
    sequence = []
    current = random.choice(valid_starts)
    
    # First note in scale
    current = (quantize(current[0], SCALE_NOTES, SCALE_ROOT), current[1])
    sequence.append(current)
    
    for _ in range(TOTAL_NOTES - 1):
        # Get possible next notes
        if current in transitions:
            candidates = transitions[current]
        else:
            # Find any transition with same pitch
            candidates = []
            for k, v in transitions.items():
                if k[0] == current[0]:
                    candidates.extend(v)
        
        if not candidates:
            candidates = valid_starts
        
        next_note = random.choice(candidates)
        
        # Just quantize to scale (don't skip)
        adjusted = quantize(next_note[0], SCALE_NOTES, SCALE_ROOT)
        sequence.append((adjusted, next_note[1]))
        current = (adjusted, next_note[1])
    
    # Save MIDI
    print(f"[OK] Saving MIDI...")
    
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = int(60000000 / BPM)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))  # Sax
    
    for note, dur in sequence:
        ticks = dur * 96
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))
        track.append(mido.Message('note_off', note=note, velocity=64, time=ticks))
    
    track.append(mido.MetaMessage('end_of_track'))
    
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    out_file = os.path.join(OUTPUT_PATH, f"ritornela_{SCALE}_{BPM}bpm_{MEASURES}m.mid")
    mid.save(out_file)
    
    print(f"\n[OK] Saved: {out_file}")
    print(f"[i] Length: {len(sequence)} notes ({MEASURES} measures)")

if __name__ == "__main__":
    main()