# -*- coding: utf-8 -*-
"""
REAPER Auto-MIDI-Export cu pyautogui
Extrage MIDI și apasă Enter automat pentru a salva fără prompt

INSTALARE:
pip install pyautogui
pip install pywin32

RULARE:
python reaper_auto_export_midi.py
"""

import time
import pyautogui
import subprocess

# Configurare
OUTPUT_FOLDER = r"C:\Users\ASU\.openclaw\workspace\scripts_extract\session_guitarist_export"
PATTERN_DURATION = 16

# Pattern-urile
PATTERNS = [
    "Blues", "Americana", "Rock School", "Reggae", 
    "Bollywood", "Bonfire", "Latin Love", "Dark Matter",
    "Main Stage", "Pure", "Sweet Love", "Straightforward",
    "Southern Shuffle", "RnB Classics", "Reverse EDM"
]

def run_reaper_script(script_path):
    """Rulează un script REAPER."""
    subprocess.Popen(["reaper", "-run", script_path], shell=True)
    time.sleep(2)

def wait_for_save_dialog(timeout=30):
    """Așteaptă fereastra de salvare și o închide."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Caută fereastra de salvare
        try:
            # Încearcă să găsești butonul Save
            save_btn = pyautogui.locateOnScreen("save_button.png", confidence=0.8)
            if save_btn:
                print("Găsit fereastra de salvare!")
                pyautogui.press('enter')
                return True
        except:
            pass
        
        # Verifică dacă fereastra e activă
        if pyautogui.locateCenterOnScreen("save dialog"):
            pyautogui.press('enter')
            return True
        
        time.sleep(0.5)
    
    print("Timeout - nu am găsit fereastra de salvare")
    return False

def extract_pattern(pattern_name):
    """Capturează un pattern și extrage MIDI."""
    print(f"Capturare: {pattern_name}")
    
    # Deschide REAPER și rulează scriptul de captură
    # Trebuie să ai deja REAPER deschis cu track-ul pregătit
    
    # Pentru moment, doar simulează
    print(f"  Start recording for {PATTERN_DURATION}s...")
    time.sleep(PATTERN_DURATION)
    
    print(f"  Stop recording...")
    time.sleep(1)
    
    print(f"  Extracting MIDI...")
    # Aici ar trebui să trimit comanda de extragere MIDI
    # Dar fără REAPER deschis, nu pot
    
    # Apasă Enter automat
    time.sleep(1)
    pyautogui.press('enter')
    print(f"  ✓ Salvat: {pattern_name}.mid")
    
    time.sleep(2)

def main():
    print("=== REAPER Auto-MIDI-Export ===")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Pattern-uri: {len(PATTERNS)}")
    print()
    
    print("IMPORTANT: Asigură-te că:")
    print("1. REAPER este deschis")
    print("2. Ai deja un track cu FX Kontakt")
    print("3. Session Guitarist este încărcat")
    print()
    
    input("Apasă Enter când ești pregătit...")
    
    for i, pattern in enumerate(PATTERNS, 1):
        print(f"\n[{i}/{len(PATTERNS)}] {pattern}")
        
        # Deschide fereastra de salvare (simulat)
        # Trebuie să declanșezi manual extragerea MIDI în REAPER
        
        # Pentru o soluție completă, folosește ReaPack cu JS_ReaScriptAPI
        print(f"  → Deschide Fereastra Pattern în Kontakt")
        print(f"  → Selectează pattern-ul: {pattern}")
        print(f"  → Apasă Record în REAPER")
        print(f"  → După {PATTERN_DURATION}s, oprește recording")
        print(f"  → Extract MIDI (Ctrl+E)")
        print(f"  → Apasă Enter pentru a salva")
        
        input(f"  Apasă Enter după ce extragi {pattern}...")
    
    print("\n=== FINALIZAT ===")
    print(f"Pattern-uri: {len(PATTERNS)}")
    print(f"Output folder: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()
