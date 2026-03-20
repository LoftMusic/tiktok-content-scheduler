# -*- coding: utf-8 -*-
"""
Testeaza unnks pentru a vedea ce contine fisierele .nkx
"""

import subprocess
import os
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

NKX_FILE = r"I:\librarii kontakt 2023\Session Guitarist - Electric Sunburst Deluxe 1.2.0 [Native Instruments]\Samples\Data\SGESD_0.nkx"
OUTPUT_DIR = r"C:\Users\ASU\.openclaw\workspace\scripts_extract\unnks_test"

def test_unnks():
    print("=" * 60)
    print("TEST UNNKS")
    print("=" * 60)
    print()
    
    unnks_path = r"C:\unnks\unnks.exe"
    if not os.path.exists(unnks_path):
        print(f"unnks.exe not found at: {unnks_path}")
        print()
        print("1. Download unnks from:")
        print("   http://downloads.sourceforge.net/unnks/unnks-0.2.3-windows.zip")
        print()
        print("2. Extract unnks.exe to C:\\unnks\\")
        print()
        print("3. Run this script again")
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    cmd_list = [unnks_path, "-t", NKX_FILE]
    print(f"[1] Listing contents of .nkx file...")
    print(f"    Command: {' '.join(cmd_list)}")
    print()
    
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
        print("OUTPUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
    except Exception as e:
        print(f"ERROR: {e}")
    
    print()
    print("=" * 60)
    print("To extract, use:")
    print(f"    unnks -xvf \"{NKX_FILE}\" -C \"{OUTPUT_DIR}\"")
    print("=" * 60)

if __name__ == "__main__":
    test_unnks()
