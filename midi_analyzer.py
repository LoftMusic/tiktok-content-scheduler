"""
MIDI Dataset Analyzer
Analizează fișierele MIDI și extrage statistici utile pentru training.
"""

import os
import mido
from collections import defaultdict
from pathlib import Path

DATASET_PATH = r"G:\MIDI PATTERNS\DATASET"

def analyze_midi(filepath):
    """Analizează un fișier MIDI și extrage metrici."""
    try:
        mid = mido.MidiFile(filepath)
        
        tempos = []
        time_signatures = []
        instruments = defaultdict(int)
        note_counts = defaultdict(int)
        total_notes = 0
        program_changes = set()
        
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempos.append(msg.tempo)
                elif msg.type == 'time_signature':
                    time_signatures.append((msg.numerator, msg.denominator))
                elif msg.type == 'program_change':
                    program_changes.add(msg.program)
                elif msg.type == 'note_on' and msg.velocity > 0:
                    note_counts[msg.note] += 1
                    total_notes += 1
        
        # Calculează BPM din tempo
        bpm = None
        if tempos:
            avg_tempo = sum(tempos) / len(tempos)
            bpm = mido.tempo2bpm(avg_tempo)
        
        # Extrage numele din filename
        filename = os.path.basename(filepath)
        
        return {
            'file': filename,
            'tracks': len(mid.tracks),
            'bpm': round(bpm, 1) if bpm else None,
            'time_sig': time_signatures[0] if time_signatures else None,
            'instruments': list(program_changes),
            'note_range': (min(note_counts.keys()), max(note_counts.keys())) if note_counts else (None, None),
            'total_notes': total_notes
        }
    except Exception as e:
        return {'file': os.path.basename(filepath), 'error': str(e)}

def main():
    files = list(Path(DATASET_PATH).glob("*.mid"))
    print(f"[+] Analizez {len(files)} fisiere MIDI...\n")
    
    results = []
    for f in files:
        result = analyze_midi(f)
        results.append(result)
    
    # Statistici
    bpms = [r['bpm'] for r in results if r.get('bpm')]
    time_sigs = [r['time_sig'] for r in results if r.get('time_sig')]
    all_instruments = []
    note_ranges = []
    
    for r in results:
        if 'instruments' in r:
            all_instruments.extend(r['instruments'])
        if r.get('note_range') and r['note_range'][0] is not None:
            note_ranges.append(r['note_range'])
    
    print("=" * 50)
    print("=== STATISTICI DATASET ===")
    print("=" * 50)
    
    if bpms:
        print(f"\n[TEMPO]")
        print(f"   Min: {min(bpms)} | Max: {max(bpms)} | Avg: {sum(bpms)/len(bpms):.1f}")
    
    if time_sigs:
        from collections import Counter
        ts_counts = Counter(time_sigs)
        print(f"\n[TIME SIGNATURES]")
        for ts, count in ts_counts.most_common():
            print(f"   {ts[0]}/{ts[1]}: {count} fisiere")
    
    if all_instruments:
        from collections import Counter
        inst_counts = Counter(all_instruments)
        # GM instrument names
        gm_names = {
            0: "Piano", 1: "Piano", 2: "Piano", 3: "Piano",
            56: "Trumpet", 57: "Trombone", 58: "Tuba",
            64: "Sax", 65: "Oboe", 66: "Flute", 67: "Clarinet",
            33: "Bass", 34: "Finger Bass", 35: "Pick Bass"
        }
        print(f"\n[INSTRUMENTS (General MIDI)]")
        for inst, count in inst_counts.most_common(10):
            name = gm_names.get(inst, f"#{inst}")
            print(f"   {name}: {count}")
    
    if note_ranges:
        all_low = [r[0] for r in note_ranges]
        all_high = [r[1] for r in note_ranges]
        # Simple note name conversion
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        def note_name(n):
            octave = n // 12 - 1
            return f"{notes[n % 12]}{octave}"
        print(f"\n[NOTE RANGE]")
        print(f"   Lowest: {min(all_low)} ({note_name(min(all_low))})")
        print(f"   Highest: {max(all_high)} ({note_name(max(all_high))})")
    
    # Erori
    errors = [r for r in results if 'error' in r]
    if errors:
        print(f"\n[ERORI]: {len(errors)} fisiere nu s-au putut citi")
    
    # Save detailed results
    output_file = Path(DATASET_PATH) / "analysis_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("MIDI Dataset Analysis\n")
        f.write("=" * 50 + "\n\n")
        for r in results:
            if 'error' not in r:
                f.write(f"{r['file']}\n")
                f.write(f"  BPM: {r.get('bpm')} | Time: {r.get('time_sig')} | Notes: {r.get('total_notes')}\n")
    
    print(f"\n[OK] Rezultatele salvate in: {output_file}")

if __name__ == "__main__":
    main()