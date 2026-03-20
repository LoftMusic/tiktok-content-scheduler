"""
Markov Chain MIDI Generator - versiune imbunatatita
Markov de ordin 2 + lungime completa (4-8 masuri)
"""

import os
import mido
import random
from collections import defaultdict
from pathlib import Path

DATASET_PATH = r"G:\MIDI PATTERNS\DATASET"
OUTPUT_PATH = r"G:\MIDI PATTERNS\GENERATED"
NOTE_DURATION = 96  # 16th notes

# Scale disponibile
SCALES = {
    'Amin': [0, 2, 3, 5, 7, 8, 10],
    'Emin': [0, 2, 3, 5, 7, 8, 10],
    'Dmin': [0, 2, 3, 5, 7, 8, 10],
    'Cmin': [0, 2, 3, 5, 7, 8, 10],
    'Bmin': [0, 2, 3, 5, 7, 8, 10],
    'Fmin': [0, 2, 3, 5, 7, 8, 10],
    'EPhyr': [0, 1, 3, 5, 7, 8, 10],
    'BPhyr': [0, 1, 3, 5, 7, 8, 10],
    'Cmaj': [0, 2, 4, 5, 7, 9, 11],
}

SCALE_ROOTS = {
    'Amin': 57, 'Emin': 52, 'Dmin': 50, 'Cmin': 48,
    'Bmin': 47, 'Fmin': 53, 'EPhyr': 52, 'BPhyr': 47,
    'Cmaj': 60,
}

class MarkovRitornela:
    def __init__(self, order=2):
        self.order = order  # Markov order
        # key: tuple of (note, duration), value: list of next (note, duration)
        self.transitions = defaultdict(list)
        self.start_sequences = []  # primele N note pentru inceput
        self.note_pitch_probs = defaultdict(list)  # probabilitati pentru note
        self.duration_probs = defaultdict(list)  # probabilitati pentru durate
        
    def is_in_scale(self, note, scale_name):
        if scale_name not in SCALES:
            return True
        root = SCALE_ROOTS.get(scale_name, 60)
        scale = SCALES[scale_name]
        rel = (note - root) % 12
        return rel in scale
    
    def quantize_to_scale(self, note, scale_name):
        if scale_name not in SCALES:
            return note
        root = SCALE_ROOTS[scale_name]
        scale = SCALES[scale_name]
        base = (note // 12) * 12
        rel = note % 12
        if rel in scale:
            return note
        closest = min(scale, key=lambda x: min(abs(x - rel), abs(x - rel + 12), abs(x - rel - 12)))
        if abs(closest + 12 - rel) < abs(closest - rel):
            closest += 12
        elif closest < rel and abs(closest - 12 - rel) < abs(closest - rel):
            closest -= 12
        return base + closest
    
    def extract_sequences(self, mid):
        """Extrage toate secventele din MIDI."""
        notes = []
        for track in mid.tracks:
            note_on_times = {}
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on_times[msg.note] = msg.time
                elif msg.type == 'note_off' and msg.note in note_on_times:
                    duration = msg.time - note_on_times[msg.note]
                    note = msg.note
                    del note_on_times[msg.note]
                    if duration < 24:
                        continue
                    duration_q = max(1, duration // NOTE_DURATION)
                    notes.append((note, duration_q))
        return notes
    
    def train(self, mid_files):
        print(f"[i] Antrenez (ord={self.order}) pe {len(mid_files)} fisiere...")
        
        all_sequences = []
        
        for filepath in mid_files:
            try:
                mid = mido.MidiFile(filepath)
                notes = self.extract_sequences(mid)
                if len(notes) >= self.order + 1:
                    all_sequences.append(notes)
                    self.start_sequences.append(tuple(notes[:self.order]))
            except:
                pass
        
        # Construieste tranzitii pentru Markov de ordin N
        for seq in all_sequences:
            for i in range(len(seq) - self.order):
                key = tuple(seq[i:i + self.order])
                next_note = seq[i + self.order]
                self.transitions[key].append(next_note)
                # Pentru probabilitati pitch
                self.note_pitch_probs[seq[i][0]].append(next_note[0])
                # Pentru probabilitati durata
                self.duration_probs[seq[i][1]].append(next_note[1])
        
        # Colecteaza toate notele pentru inceput
        all_notes = [n for seq in all_sequences for n in seq]
        self.all_pitches = [n[0] for n in all_notes]
        self.all_durations = [n[1] for n in all_notes]
        
        print(f"[OK] {len(self.transitions)} stari, {len(all_notes)} note")
    
    def generate(self, length=32, scale_name='Emin', min_note=48, max_note=84):
        """Genereaza secventa cu coventa."""
        if not self.start_sequences:
            return []
        
        # Incepe cu o secventa de inceput
        current = list(random.choice(self.start_sequences))
        sequence = list(current)
        
        while len(sequence) < length:
            key = tuple(current[-self.order:])
            
            if key in self.transitions:
                candidates = self.transitions[key]
            else:
                # Fallback: orice tranzitie partiala
                candidates = []
                for k in self.transitions:
                    if k[-1] == key[-1]:
                        candidates.extend(self.transitions[k])
                if not candidates:
                    candidates = [(random.choice(self.all_pitches), random.choice(self.all_durations))]
            
            next_note = random.choice(candidates)
            
            # Verificam scala si registrul
            if self.is_in_scale(next_note[0], scale_name) and min_note <= next_note[0] <= max_note:
                adjusted = self.quantize_to_scale(next_note[0], scale_name)
                sequence.append((adjusted, next_note[1]))
                current.append((adjusted, next_note[1]))
                current = current[-self.order:]
        
        return sequence[:length]
    
    def save_midi(self, sequence, filename, bpm=100, instrument=65):
        """Salveaza MIDI."""
        mid = mido.MidiFile(type=0)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        tempo = int(60000000 / bpm)
        
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
        track.append(mido.Message('program_change', program=instrument, channel=0))
        
        for note, duration in sequence:
            ticks = duration * NOTE_DURATION
            track.append(mido.Message('note_on', note=note, velocity=100, time=0))
            track.append(mido.Message('note_off', note=note, velocity=64, time=ticks))
        
        track.append(mido.MetaMessage('end_of_track'))
        
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        output_file = os.path.join(OUTPUT_PATH, filename)
        mid.save(output_file)
        return output_file

def main():
    # Setari
    TARGET_BPM = 100
    TARGET_SCALE = 'Emin'
    NUM_VARIATIONS = 4
    
    # 4 masuri = 16 beats = 64 16th notes (cu NOTE_DURATION=96)
    # 8 masuri = 32 beats
    MEASURES = 8
    
    print(f"[i] Setari: BPM={TARGET_BPM}, Scala={TARGET_SCALE}, Masuri={MEASURES}")
    
    dataset_files = list(Path(DATASET_PATH).glob("*.mid"))
    print(f"[i] Gasit {len(dataset_files)} fisiere")
    
    if not dataset_files:
        return
    
    # Antrenare Markov order 2
    model = MarkovRitornela(order=2)
    model.train(dataset_files)
    
    # Calculam lungimea (16th notes)
    notes_per_measure = 4 * 4  # 4 beats * 4 16th per beat
    total_notes = MEASURES * notes_per_measure
    
    print(f"\n[>] Generez {NUM_VARIATIONS} ritornele ({MEASURES} masuri = {total_notes} note)...")
    
    for i in range(NUM_VARIATIONS):
        sequence = model.generate(
            length=total_notes,
            scale_name=TARGET_SCALE,
            min_note=50,
            max_note=84
        )
        
        filename = f"ritornela_{TARGET_SCALE}_{TARGET_BPM}bpm_{MEASURES}m_{i+1:02d}.mid"
        model.save_midi(sequence, filename, bpm=TARGET_BPM)
        print(f"  [{i+1}] {filename} - {len(sequence)} note")
    
    print(f"\n[OK] {OUTPUT_PATH}")

if __name__ == "__main__":
    main()