# -*- coding: utf-8 -*-
"""
Session Guitarist Pattern Extractor v2
Extrage metadata despre pattern-urile din librăria Session Guitarist

NOTĂ: Pentru a extrage pattern-uri MIDI REALE din fișierele .nki/.nksn:
1. Ai nevoie de Kontakt FULL (nu Player)
2. Deschide librăria în Kontakt
3. Selectează snapshot-ul dorit
4. Folosește 'Export Pattern' din meniul Kontakt
5. Sau folosește ni-extractor (https://github.com/azurite13/nkx)

Acest script extrage metadata și listează toate pattern-urile disponibile.
"""

import os
import sys
import json
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Calea către librăria Session Guitarist
LIBRARY_PATH = r"I:\librarii kontakt 2023\Session Guitarist - Electric Sunburst Deluxe 1.2.0 [Native Instruments]"

# Output folder
OUTPUT_PATH = r"C:\Users\ASU\.openclaw\workspace\scripts_extract\session_guitarist_patterns"

def get_all_snapshots():
    """Obține toate snapshot-urile disponibile."""
    snapshots = []
    
    snapshots_folder = os.path.join(LIBRARY_PATH, "Snapshots")
    
    if not os.path.exists(snapshots_folder):
        print(f"[ERROR] Folderul de snapshoturi nu exista: {snapshots_folder}")
        return []
    
    for root, dirs, files in os.walk(snapshots_folder):
        for file in files:
            if file.endswith('.nksn'):
                full_path = os.path.join(root, file)
                folder_name = os.path.basename(root)
                # Extract pattern name (remove suffix like " (Melody)")
                pattern_name = file.replace('.nksn', '')
                
                snapshots.append({
                    'name': pattern_name,
                    'folder': folder_name,
                    'path': full_path,
                    'size': os.path.getsize(full_path)
                })
    
    return snapshots

def get_all_instruments():
    """Obține toate instrumentele disponibile."""
    instruments = []
    
    instruments_folder = os.path.join(LIBRARY_PATH, "Instruments")
    
    if not os.path.exists(instruments_folder):
        print(f"[ERROR] Folderul de instrumente nu exista: {instruments_folder}")
        return []
    
    for root, dirs, files in os.walk(instruments_folder):
        for file in files:
            if file.endswith('.nki'):
                full_path = os.path.join(root, file)
                instruments.append({
                    'name': file.replace('.nki', ''),
                    'path': full_path,
                    'size': os.path.getsize(full_path)
                })
    
    return instruments

def get_midi_files():
    """Obține toate fișierele MIDI din librărie."""
    midi_files = []
    
    for root, dirs, files in os.walk(LIBRARY_PATH):
        for file in files:
            if file.lower().endswith('.mid'):
                full_path = os.path.join(root, file)
                midi_files.append({
                    'name': file,
                    'path': full_path,
                    'size': os.path.getsize(full_path),
                    'folder': os.path.relpath(root, LIBRARY_PATH)
                })
    
    return midi_files

def main():
    print("=" * 60)
    print("Session Guitarist Pattern Extractor v2")
    print("=" * 60)
    print()
    
    # Output folder
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    # 1. Găsește snapshot-urile
    print("[1] Caut snapshot-uri...")
    snapshots = get_all_snapshots()
    print(f"    Gasit: {len(snapshots)} snapshot-uri")
    print()
    
    # Salvează snapshot-urile
    snapshots_file = os.path.join(OUTPUT_PATH, 'snapshots.json')
    with open(snapshots_file, 'w', encoding='utf-8') as f:
        json.dump(snapshots, f, indent=2, ensure_ascii=False)
    print(f"    [OK] Salvat: {snapshots_file}")
    
    # 2. Găsește instrumentele
    print()
    print("[2] Caut instrumente...")
    instruments = get_all_instruments()
    print(f"    Gasit: {len(instruments)} instrumente")
    print()
    
    # Salvează instrumentele
    instruments_file = os.path.join(OUTPUT_PATH, 'instruments.json')
    with open(instruments_file, 'w', encoding='utf-8') as f:
        json.dump(instruments, f, indent=2, ensure_ascii=False)
    print(f"    [OK] Salvat: {instruments_file}")
    
    # 3. Găsește fișierele MIDI
    print()
    print("[3] Caut fisiere MIDI...")
    midi_files = get_midi_files()
    print(f"    Gasit: {len(midi_files)} fisiere MIDI")
    print()
    
    for mf in midi_files:
        print(f"    - {mf['name']} ({mf['folder']}) - {mf['size']} bytes")
    
    # Salvează fișierele MIDI
    if midi_files:
        midi_file = os.path.join(OUTPUT_PATH, 'midi_files.json')
        with open(midi_file, 'w', encoding='utf-8') as f:
            json.dump(midi_files, f, indent=2, ensure_ascii=False)
        print(f"    [OK] Salvat: {midi_file}")
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Snapshot-uri: {len(snapshots)}")
    print(f"  Instrumente:  {len(instruments)}")
    print(f"  MIDI files:   {len(midi_files)}")
    print()
    
    print("=" * 60)
    print("HOW TO EXTRACT MIDI PATTERNS")
    print("=" * 60)
    print()
    print("Pentru a extrage pattern-urile MIDI REALE:")
    print()
    print("1. DESCHIDE LIBRARIA ÎN KONTAKT (version FULL, nu Player)")
    print("   - Start Kontakt")
    print("   - Deschide 'Session Guitarist - Electric Sunburst Deluxe'")
    print()
    print("2. SELECTEAZĂ UN SNAPSHOT")
    print("   - În sidebar stânga, alege un snapshot (ex: 'Blues')")
    print("   - Patternul se va încărca")
    print()
    print("3. EXPORTĂ PATTERNUL")
    print("   - Apasă butonul 'Pattern' în partea de sus")
    print("   - Apasă 'Export Pattern' din meniul Pattern")
    print("   - Alege locația și formatul (MIDI)")
    print("   - Salvează")
    print()
    print("ALTERNATIV (fără Kontakt full):")
    print("   - Folosește tool-ul nkx:")
    print("     https://github.com/azurite13/nkx")
    print()
    print("   - Sau convertitor online:")
    print("     https://www.niktomm.com/nki-extractor/")
    print()
    print("[OK] Done!")

if __name__ == "__main__":
    main()
