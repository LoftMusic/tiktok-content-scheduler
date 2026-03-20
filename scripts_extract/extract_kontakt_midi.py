# -*- coding: utf-8 -*-
"""
Extraște pattern-uri MIDI din Session Guitarist (fără REAPER)

 caută fișiere .mid în librărie și le copiază în folderul de output
"""

import os
import sys
import shutil
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Calea către librăria Session Guitarist
LIBRARY_PATH = r"I:\librarii kontakt 2023\Session Guitarist - Electric Sunburst Deluxe 1.2.0 [Native Instruments]"

# Folderul de output
OUTPUT_FOLDER = r"C:\Users\ASU\.openclaw\workspace\scripts_extract\session_guitarist_export"

def find_midi_files():
    """Caută toate fișierele .mid în librărie."""
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

def find_nki_files():
    """Caută toate fișierele .nki (Kontakt instruments)."""
    nki_files = []
    
    for root, dirs, files in os.walk(LIBRARY_PATH):
        for file in files:
            if file.lower().endswith('.nki'):
                full_path = os.path.join(root, file)
                nki_files.append({
                    'name': file,
                    'path': full_path,
                    'size': os.path.getsize(full_path),
                    'folder': os.path.relpath(root, LIBRARY_PATH)
                })
    
    return nki_files

def find_nksn_files():
    """Caută toate fișierele .nksn (Kontakt snapshots)."""
    nksn_files = []
    
    for root, dirs, files in os.walk(LIBRARY_PATH):
        for file in files:
            if file.lower().endswith('.nksn'):
                full_path = os.path.join(root, file)
                nksn_files.append({
                    'name': file,
                    'path': full_path,
                    'size': os.path.getsize(full_path),
                    'folder': os.path.relpath(root, LIBRARY_PATH)
                })
    
    return nksn_files

def copy_midi_files(midi_files):
    """Copiază fișierele .mid în folderul de output."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    copied = []
    for mf in midi_files:
        src = mf['path']
        dst = os.path.join(OUTPUT_FOLDER, mf['name'])
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            copied.append(mf['name'])
            print(f"  Copied: {mf['name']} ({mf['size']} bytes)")
    
    return copied

def main():
    print("=" * 60)
    print("EXTRACT MIDI FROM SESSION GUITARIST")
    print("=" * 60)
    print()
    
    # 1. Caută fișiere .mid
    print("[1] Looking for .mid files in library...")
    midi_files = find_midi_files()
    print(f"  Found: {len(midi_files)} .mid files")
    
    for mf in midi_files:
        print(f"    - {mf['name']} ({mf['folder']})")
    print()
    
    # 2. Caută fișiere .nki
    print("[2] Looking for .nki files...")
    nki_files = find_nki_files()
    print(f"  Found: {len(nki_files)} .nki files")
    
    for nf in nki_files:
        print(f"    - {nf['name']} ({nf['folder']})")
    print()
    
    # 3. Caută fișiere .nksn
    print("[3] Looking for .nksn files...")
    nksn_files = find_nksn_files()
    print(f"  Found: {len(nksn_files)} .nksn files (snapshots)")
    print()
    
    # 4. Copiază fișierele .mid
    if midi_files:
        print("[4] Copying .mid files...")
        copied = copy_midi_files(midi_files)
        print(f"  Copied: {len(copied)} files")
    else:
        print("[4] No .mid files found in library.")
        print()
        print("  NOTE: Session Guitarist stores patterns inside .nki/.nksn files")
        print("  To extract them, you need:")
        print()
        print("  OPTION A: KONTAKT FULL (not Player)")
        print("     1. Open Session Guitarist in Kontakt")
        print("     2. Select a snapshot/preset")
        print("     3. Click 'Pattern' button in top bar")
        print("     4. Click 'Export Pattern' -> Save as .mid")
        print()
        print("  OPTION B: Use nkx tool (unofficial)")
        print("     - https://github.com/azurite13/nkx")
        print("     - https://github.com/reaper-verse/nikki")
        print()
    
    # 5. Summary
    print("=" * 60)
    print(f"Output folder: {OUTPUT_FOLDER}")
    print("=" * 60)
    print()
    
    # Listează ce e în output folder
    if os.path.exists(OUTPUT_FOLDER):
        files = os.listdir(OUTPUT_FOLDER)
        if files:
            print("Files in output folder:")
            for f in files:
                path = os.path.join(OUTPUT_FOLDER, f)
                size = os.path.getsize(path)
                print(f"  - {f} ({size} bytes)")
        else:
            print("Output folder is empty (no .mid files found in library)")
    else:
        print("Output folder not created")

if __name__ == "__main__":
    main()
