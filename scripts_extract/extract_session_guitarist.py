# -*- coding: utf-8 -*-
"""
Session Guitarist Pattern Extractor
Extrage pattern-uri MIDI din librăriile Native Instruments Session Guitarist

NOTĂ: Pentru a extrage pattern-uri reale (nu doar metadata), ai nevoie de:
1. Kontakt full version (nu doar player)
2. Scripturi NI sau tooluri externe care să interactieze cu Kontakt API

Acest script extrage metadata despre pattern-uri (nume, tonalitate, BPM etc.)
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Calea către librăria Session Guitarist
LIBRARY_PATH = r"I:\librarii kontakt 2023\Session Guitarist - Electric Sunburst Deluxe 1.2.0 [Native Instruments]"

# Output folder
OUTPUT_PATH = r"C:\Users\ASU\.openclaw\workspace\scripts_extract\session_guitarist_patterns"

def extract_metadata_from_folder(folder_path):
    """Extrage metadata din folderele librăriei."""
    metadata = {
        'folder': os.path.basename(folder_path),
        'path': str(folder_path),
        'files': [],
        'info': {}
    }
    
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            if os.path.isfile(item_path):
                ext = os.path.splitext(item)[1].lower()
                metadata['files'].append({
                    'name': item,
                    'extension': ext,
                    'size': os.path.getsize(item_path)
                })
                
                # Caută fișiere de tip .nki (Kontakt instrument)
                if ext == '.nki':
                    metadata['info']['nki_files'] = metadata['info'].get('nki_files', [])
                    metadata['info']['nki_files'].append(item)
                    
                # Caută fișiere .nkm (Kontakt module/macro)
                elif ext == '.nkm':
                    metadata['info']['nkm_files'] = metadata['info'].get('nkm_files', [])
                    metadata['info']['nkm_files'].append(item)
                    
            elif os.path.isdir(item_path) and not item.startswith('.'):
                # Recursiv pentru folderele copil
                sub_metadata = extract_metadata_from_folder(item_path)
                if sub_metadata['files'] or sub_metadata['info']:
                    metadata['info'].setdefault('subfolders', []).append(sub_metadata)
    
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata

def analyze_session_guitarist_patterns():
    """Analizează structura librăriei Session Guitarist."""
    
    print("[+] Analizez libraria Session Guitarist...")
    print(f"    Path: {LIBRARY_PATH}")
    print()
    
    # Verifică dacă folderul există
    if not os.path.exists(LIBRARY_PATH):
        print(f"[ERROR] Folderul nu exista: {LIBRARY_PATH}")
        return None
    
    # Creează output folder
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    # Extrage metadata
    metadata = extract_metadata_from_folder(LIBRARY_PATH)
    
    # Salvează metadata în JSON
    output_file = os.path.join(OUTPUT_PATH, 'patterns_metadata.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Metadata salvat: {output_file}")
    
    # Afișează un summary
    print()
    print("=" * 60)
    print("=== SUMMARY ===")
    print("=" * 60)
    
    nki_count = len(metadata['info'].get('nki_files', []))
    nkm_count = len(metadata['info'].get('nkm_files', []))
    print(f"  .nki files: {nki_count}")
    print(f"  .nkm files: {nkm_count}")
    print(f"  Subfoldere: {len(metadata['info'].get('subfolders', []))}")
    
    # Afișează fișierele găsite
    if metadata['info'].get('nki_files'):
        print()
        print("  NKI files:")
        for f in metadata['info']['nki_files'][:10]:  # First 10
            print(f"    - {f}")
        if len(metadata['info']['nki_files']) > 10:
            print(f"    ... si {len(metadata['info']['nki_files']) - 10} mai multe")
    
    if metadata['info'].get('subfolders'):
        print()
        print("  Subfoldere:")
        for sf in metadata['info']['subfolders'][:10]:
            print(f"    - {sf['folder']} ({len(sf['files'])} fisiere)")
        if len(metadata['info']['subfolders']) > 10:
            print(f"    ... si {len(metadata['info']['subfolders']) - 10} mai multe")
    
    print()
    print("=" * 60)
    print("NOTE:")
    print("=" * 60)
    print("Pentru a extrage pattern-uri MIDI REALE din Session Guitarist:")
    print()
    print("1. Deschide librăria în Kontakt (version FULL, nu Player)")
    print("2. Selectează pattern-ul dorit")
    print("3. Folosește 'Export Pattern' din meniul Kontakt")
    print("4. Sau folosește ni-extractor tool (vezi link de mai jos)")
    print()
    print("Link util: https://github.com/azurite13/nkx (NKI/NKM extractor)")
    print()
    
    return metadata

def main():
    metadata = analyze_session_guitarist_patterns()
    
    if metadata:
        print("\n[OK] Analiza finalizata!")
    else:
        print("\n[ERROR] Analiza a esuat!")

if __name__ == "__main__":
    main()
