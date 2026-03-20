# -*- coding: utf-8 -*-
"""
Guitar Pattern Extractor
Filtrează fișierele MIDI care conțin pattern-uri de chitară
"""

import os
import sys
import mido
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATASET_DIR = r"G:\MIDI PATTERNS\DATASET"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GUITAR_PATTERNS"

# GM instrument numbers for guitar
GUITAR_PROGRAMS = {
    24: "Acoustic Guitar (nylon)",
    25: "Acoustic Guitar (steel)",
    26: "Electric Guitar (jazz)",
    27: "Electric Guitar (clean)",
    28: "Electric Guitar (muted)",
    29: "Overdriven Guitar",
    30: "Distortion Guitar",
    31: "Guitar Harmonics",
}

def is_guitar_track(track):
    """Check if track is likely a guitar track."""
    for msg in track:
        if msg.type == 'program_change':
            if msg.program in GUITAR_PROGRAMS:
                return True, GUITAR_PROGRAMS[msg.program]
    return False, None

def analyze_midi(filepath):
    """Analyze MIDI file for guitar content."""
    try:
        mid = mido.MidiFile(filepath)
        
        guitar_found = False
        guitar_instrument = None
        total_notes = 0
        guitar_notes = 0
        has_strumming_pattern = False
        
        for track in mid.tracks:
            is_guitar, instrument = is_guitar_track(track)
            
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    total_notes += 1
                    if is_guitar:
                        guitar_notes += 1
        
        if guitar_notes > total_notes * 0.5:  # Majoritatea notele sunt de chitară
            guitar_found = True
        
        return {
            'file': os.path.basename(filepath),
            'guitar_found': guitar_found,
            'guitar_instrument': guitar_instrument,
            'total_notes': total_notes,
            'guitar_notes': guitar_notes,
        }
    except Exception as e:
        return {'file': os.path.basename(filepath), 'error': str(e)}

def main():
    print("=" * 60)
    print("GUITAR PATTERN EXTRACTOR")
    print("=" * 60)
    print()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all MIDI files
    midi_files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"Found {len(midi_files)} MIDI files")
    print()
    
    # Analyze each file
    guitar_files = []
    
    for i, f in enumerate(midi_files):
        result = analyze_midi(f)
        
        if result.get('error'):
            print(f"[!] {result['file']}: {result['error']}")
        elif result.get('guitar_found'):
            print(f"[GUITAR] {result['file']} ({result['guitar_notes']}/{result['total_notes']} notes)")
            guitar_files.append(f)
        else:
            # Verifică dacă are note în gamă de chitară (E2-E4)
            try:
                mid = mido.MidiFile(f)
                notes = []
                for track in mid.tracks:
                    for msg in track:
                        if msg.type == 'note_on' and msg.velocity > 0:
                            notes.append(msg.note)
                
                # Guitar range: E2 (40) to E4 (64) mostly
                guitar_range_notes = [n for n in notes if 40 <= n <= 72]
                if len(guitar_range_notes) > len(notes) * 0.5:
                    print(f"[GUITAR-RANGE] {result['file']} (guitar-range notes: {len(guitar_range_notes)})")
                    guitar_files.append(f)
            except:
                pass
    
    print()
    print("=" * 60)
    print(f"Found {len(guitar_files)} files with guitar content")
    
    # Copy guitar files to output folder
    print()
    print("Copying guitar files...")
    for f in guitar_files:
        dest = os.path.join(OUTPUT_DIR, os.path.basename(f))
        if not os.path.exists(dest):
            import shutil
            shutil.copy2(f, dest)
            print(f"  Copied: {os.path.basename(f)}")
    
    print()
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
