"""
Markov Generator cu Progresii de Acorduri
Suporta diferite tonalitati si progresii
"""

import os
import mido
import random
from collections import defaultdict
from pathlib import Path

DATASET_PATH = r"G:\MIDI PATTERNS\DATASET"
OUTPUT_PATH = r"G:\MIDI PATTERNS\GENERATED"

# Tonalitati disponibile (root + scale)
KEYS = {
    'Amin': {'root': 57, 'scale': [0, 2, 3, 5, 7, 8, 10]},       # A, B, C, D, E, F, G
    'Emin': {'root': 52, 'scale': [0, 2, 3, 5, 7, 8, 10]},       # E, F#, G, A, B, C, D
    'Dmin': {'root': 50, 'scale': [0, 2, 3, 5, 7, 8, 10]},       # D, E, F, G, A, Bb, C
    'Cmin': {'root': 48, 'scale': [0, 2, 3, 5, 7, 8, 10]},       # C, D, Eb, F, G, Ab, Bb
    'Bmin': {'root': 47, 'scale': [0, 2, 3, 5, 7, 8, 10]},       # B, C#, D, E, F#, G, A
    'Fmin': {'root': 53, 'scale': [0, 2, 3, 5, 7, 8, 10]},       # F, G, Ab, Bb, C, Db, Eb
    'Cmaj': {'root': 60, 'scale': [0, 2, 4, 5, 7, 9, 11]},       # C, D, E, F, G, A, B
    'Dmaj': {'root': 62, 'scale': [0, 2, 4, 5, 7, 9, 11]},       # D, E, F#, G, A, B, C#
    'Gmaj': {'root': 67, 'scale': [0, 2, 4, 5, 7, 9, 11]},       # G, A, B, C, D, E, F#
}

# Acorduri pentru fiecare treapta (in semitonuri de la root)
# Minor: root, +3, +7 | Major: root, +4, +7
CHORDS = {
    'i': [0, 3, 7],      # minor
    'ii': [0, 2, 7],     # minor (in major e major)
    'III': [0, 3, 7],    # minor
    'IV': [0, 4, 7],     # major
    'V': [0, 4, 7],      # major  
    'VI': [0, 3, 7],     # minor
    'VII': [0, 4, 7],    # major (sau diminished)
    'iii': [0, 3, 7],
    'vi': [0, 3, 7],
    'vii': [0, 4, 7],
}

# Progresii populare
PROGRESSIONS = {
    'i_IV_III_VII': ['i', 'IV', 'III', 'VII'],           # A min - F maj - C maj - G maj
    'i_VI_IV_V': ['i', 'VI', 'IV', 'V'],                  # Classic minor
    'i_iv_VI_V': ['i', 'iv', 'VI', 'V'],                  # Minor with iv
    'i_VII_VI_V': ['i', 'VII', 'VI', 'V'],                # Andalusian
    'I_IV_V_I': ['I', 'IV', 'V', 'I'],                    # Classic major
    'I_V_vi_IV': ['I', 'V', 'vi', 'IV'],                  # Pop progression
    'i_iv_v_i': ['i', 'iv', 'v', 'i'],                    # Minor 4
}

def get_chord_notes(chord_name, key_name, octave=3):
    """Returneaza notele disponibile pentru un acord."""
    key = KEYS[key_name]
    root = key['root']
    chord_offsets = CHORDS.get(chord_name, [0, 4, 7])
    
    notes = []
    for offset in chord_offsets:
        # Add in multiple octaves
        for o in [octave - 1, octave, octave + 1]:
            note = root + offset + (o * 12)
            if 36 <= note <= 96:  # Valid range
                notes.append(note)
    return notes

def note_fits_chord(note, chord_notes):
    """Verifica daca o nota face parte din acord."""
    return any(abs(note - cn) % 12 == 0 for cn in chord_notes)

def quantize_to_chord(note, chord_notes):
    """Ajusta nota sa fie in acord."""
    if note_fits_chord(note, chord_notes):
        return note
    
    # Find closest note in chord
    best = min(chord_notes, key=lambda x: min(abs(note - x), abs(note - x - 12), abs(note - x + 12)))
    return best

def main():
    # === SETARI ===
    KEY = 'Amin'           # Tonalitate
    PROG_NAME = 'i_IV_III_VII'  # Nume progresie
    PROG = PROGRESSIONS[PROG_NAME]  # Progresia efectivă
    BPM = 100
    MEASURES_PER_CHORD = 2  # Cate masuri per acord
    NUM_VARIATIONS = 3
    
    print(f"[i] Tonalitate: {KEY}")
    print(f"[i] Progresie: {' - '.join(PROG)}")
    print(f"[i] BPM: {BPM}")
    
    # Load dataset
    files = list(Path(DATASET_PATH).glob("*.mid"))
    print(f"[i] Loading {len(files)} files...")
    
    # Extract notes
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
                        if dur >= 48:
                            d = max(1, dur // 96)
                            all_notes.append((msg.note, d))
        except:
            pass
    
    print(f"[OK] {len(all_notes)} notes extracted")
    
    if len(all_notes) < 10:
        print("[!] Not enough data!")
        return
    
    # Transitions
    transitions = defaultdict(list)
    for i in range(len(all_notes) - 1):
        transitions[all_notes[i]].append(all_notes[i + 1])
    
    # Generate
    NOTES_PER_MEASURE = 16
    NOTES_PER_CHORD = MEASURES_PER_CHORD * NOTES_PER_MEASURE
    TOTAL_NOTES = len(PROG) * NOTES_PER_CHORD
    
    print(f"[>] Generating {TOTAL_NOTES} notes ({len(PROG)} chords x {MEASURES_PER_CHORD} measures)...")
    
    for var in range(NUM_VARIATIONS):
        sequence = []
        
        for chord_idx, chord_name in enumerate(PROG):
            # Get notes for this chord
            chord_notes = get_chord_notes(chord_name, KEY, octave=3)
            
            # Valid transitions that fit in this chord
            valid_starts = [(n, d) for n, d in all_notes 
                           if note_fits_chord(n, chord_notes)]
            if not valid_starts:
                valid_starts = all_notes[:20]
            
            # Start with a chord note
            start = random.choice(valid_starts)
            start_adj = quantize_to_chord(start[0], chord_notes)
            current = (start_adj, start[1])
            sequence.append(current)
            
            # Generate notes for this chord section
            for _ in range(NOTES_PER_CHORD - 1):
                if current in transitions:
                    candidates = transitions[current]
                else:
                    candidates = valid_starts
                
                if not candidates:
                    candidates = valid_starts
                
                next_note = random.choice(candidates)
                adjusted = quantize_to_chord(next_note[0], chord_notes)
                sequence.append((adjusted, next_note[1]))
                current = (adjusted, next_note[1])
        
        # Save MIDI
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
        out_file = os.path.join(OUTPUT_PATH, f"ritornela_{KEY}_{PROG_NAME}_{BPM}bpm_v{var+1}.mid")
        mid.save(out_file)
        
        print(f"  [{var+1}] {out_file}")
    
    print(f"\n[OK] Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()