# -*- coding: utf-8 -*-
"""
Send MIDI to Kontakt to Select Patterns Automatically

Acest script trimite comenzi MIDI la Kontakt pentru a selecta pattern-urile
din Session Guitarist fără interacțiune manuală.

NOTĂ: Necesită:
1. Un MIDI Virtual Port (ex: LoopMIDI, MIDI-OX)
2. Kontakt configurat să primească MIDI de pe acel port
3. Python cu librăria `mido`

INSTALARE:
pip install mido
pip install pyserial

FOLOSIRE:
python send_kontakt_midi.py --port "LoopMIDI" --pattern "Blues"
"""

import argparse
import time
import sys
import mido
from mido import Message, MidiFile, MidiTrack

# Pattern-urile disponibile și codurile lor MIDI
# Acestea sunt codurile aproximative pentru Session Guitarist
PATTERN_CODES = {
    "Blues": {"note": 60, "velocity": 100},
    "Americana": {"note": 62, "velocity": 100},
    "Rock School": {"note": 64, "velocity": 100},
    "Reggae": {"note": 65, "velocity": 100},
    "Bollywood": {"note": 67, "velocity": 100},
    "Bonfire": {"note": 69, "velocity": 100},
    "Latin Love": {"note": 71, "velocity": 100},
    "Dark Matter": {"note": 72, "velocity": 100},
    "Main Stage": {"note": 74, "velocity": 100},
    "Pure": {"note": 76, "velocity": 100},
    "Sweet Love": {"note": 77, "velocity": 100},
    "Straightforward": {"note": 79, "velocity": 100},
    "Southern Shuffle": {"note": 81, "velocity": 100},
    "RnB Classics": {"note": 83, "velocity": 100},
    "Reverse EDM": {"note": 84, "velocity": 100},
    "3-4 Arpeggio": {"note": 48, "velocity": 100},
    "Flageolet Arpeggio": {"note": 50, "velocity": 100},
    "Hit Factor": {"note": 52, "velocity": 100},
    "Hot Funk": {"note": 53, "velocity": 100},
    "Ibiza": {"note": 55, "velocity": 100},
}

# Gama completă de pattern-uri
ALL_PATTERNS = list(PATTERN_CODES.keys())


def send_pattern_note(port_name, pattern_name, channel=0):
    """Trimite un note MIDI pentru a selecta un pattern."""
    if pattern_name not in PATTERN_CODES:
        print(f"[ERROR] Pattern necunoscut: {pattern_name}")
        print(f"    Available: {', '.join(ALL_PATTERNS)}")
        return False
    
    code = PATTERN_CODES[pattern_name]
    
    try:
        # Deschide portul MIDI
        with mido.open_output(port_name) as port:
            print(f"[OK] Conectat la port: {port_name}")
            
            # Trimite Note On
            msg = Message('note_on', note=code['note'], velocity=code['velocity'], channel=channel)
            port.send(msg)
            print(f"[SEND] Note On: {pattern_name} (note={code['note']}, vel={code['velocity']})")
            
            # Așteaptă puțin
            time.sleep(0.1)
            
            # Trimite Note Off
            msg = Message('note_off', note=code['note'], velocity=0, channel=channel)
            port.send(msg)
            print(f"[SEND] Note Off: {pattern_name}")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Nu pot deschide portul {port_name}: {e}")
        print("    Verifică dacă portul există și este deschis.")
        return False


def send_pattern_list(port_name, patterns, delay=1.0):
    """Trimite mai multe pattern-uri la rând."""
    success = 0
    total = len(patterns)
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n[{i}/{total}] Trimit pattern: {pattern}")
        
        if send_pattern_note(port_name, pattern):
            success += 1
            print(f"    ✓ Ales {pattern}")
        else:
            print(f"    ✗ Eroare la {pattern}")
        
        # Așteaptă între pattern-uri
        if i < total:
            print(f"    Aștept {delay}s...")
            time.sleep(delay)
    
    print(f"\n=== FINALIZAT ===")
    print(f"Pattern-uri trimise: {success}/{total}")
    
    return success == total


def list_available_ports():
    """Listează toate porturile MIDI disponibile."""
    print("=== PORTURI MIDI DISPONIBILE ===")
    
    for port in mido.get_output_names():
        print(f"  - {port}")
    
    print("\nDacă nu vezi portul tău, asigură-te că:")
    print("  1. LoopMIDI sau alte porturi virtuale sunt instalate")
    print("  2. Kontakt este configurat să folosească acel port")
    print("  3. Portul nu este folosit de alta aplicație")


def main():
    parser = argparse.ArgumentParser(
        description="Trimite comenzi MIDI la Kontakt pentru a selecta pattern-uri"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=str,
        help="Numele portului MIDI de ieșire (ex: LoopMIDI, VirtualMIDISynth)"
    )
    
    parser.add_argument(
        "--pattern", "-n",
        type=str,
        help="Numele pattern-ului (ex: Blues, Americana)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Listează toate pattern-urile disponibile"
    )
    
    parser.add_argument(
        "--list-ports", "-L",
        action="store_true",
        help="Listează toate porturile MIDI disponibile"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Trimite toate pattern-urile"
    )
    
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=1.0,
        help="Delay între pattern-uri (secunde)"
    )
    
    args = parser.parse_args()
    
    # ListPorts
    if args.list_ports:
        list_available_ports()
        return
    
    # List patterns
    if args.list:
        print("=== PATTERN-URI DISPONIBILE ===")
        for p in ALL_PATTERNS:
            code = PATTERN_CODES[p]
            print(f"  {p:25} -> note={code['note']:3}, velocity={code['velocity']}")
        return
    
    # Fără argumente - afișează help
    if not args.port:
        parser.print_help()
        return
    
    # Send single pattern
    if args.pattern:
        send_pattern_note(args.port, args.pattern)
        return
    
    # Send all patterns
    if args.all:
        send_pattern_list(args.port, ALL_PATTERNS, args.delay)
        return
    
    print("[ERROR] Trebuie să specifici --pattern sau --all")
    parser.print_help()


if __name__ == "__main__":
    main()
