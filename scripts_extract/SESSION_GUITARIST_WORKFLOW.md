# Workflow: Capturare Pattern-uri Session Guitarist în REAPER

## Ce Ai Nevoie:

1. **REAPER** (v6 sau mai nou)
2. **Kontakt 7** (sau versiunea ta)
3. **Session Guitarist - Electric Sunburst Deluxe** librăria
4. **Python** (pentru scripturile automate)

---

## Opțiunea 1: Metoda Manuală (Cel mai sigur)

## Pas cu Pas:

### 1. Setup în REAPER

1. Deschide REAPER
2. Creează un **Track nou** (Ctrl+T)
3. În Track 1, dă click pe `FX`
4. Selectează `Add FX` → Caută `Kontakt 7`
5. În Kontakt, deschide librăria:
   - Libraries → Session Guitarist → Electric Sunburst Deluxe
   - Selectează orice preset (ex: `Blues`)

### 2. Configurare Recording

1. **Arm track-ul pentru recording:**
   - Dă click pe butonul `R` (Record Arm) de pe track
   - Apare un patrat roșu

2. **Setează output-ul:**
   - În track, setează `I/O` → `Output` → `Master`
   - Asigură-te că sunetul vine în REAPER

### 3. Capturare Pattern Manual

1. **În Kontakt:**
   - Dă click pe butonul `Pattern` (în partea de sus)
   - Alege un pattern din listă (ex: `Americana`)

2. **În REAPER:**
   - Apasă `Record` (butonul R de pe track sau Ctrl+R global)
   - Pattern-ul va fi înregistrat în clip
   - După 1-2 secunde, apasă `Stop`

3. **Extrage MIDI:**
   - Click dreapta pe clip → `Item properties`
   - Dă click pe `Extract MIDI from item`
   - Sau folosește shortcut: **Ctrl+E**

4. **Salvează:**
   - Fișierul MIDI va fi salvat în `Media` folderul REAPER
   - Redenumește-l după pattern (ex: `Americana.mid`)

### 4. Metoda Automată - Opțiunea A: ReaScript

Scriptul `reaper_auto_capture.lua` funcționează în mod **manual controlat**:
- Îți spune ce pattern să alegi în Kontakt
- Apoi capturează automat în REAPER

**Locație:** `scripts_extract\reaper_auto_capture.lua`

**Pentru a-l folosi:**
1. În REAPER: `Extensions > ReaScript > Run script`
2. Selectează fișierul `reaper_auto_capture.lua`
3. Urmărește instrucțiunile din consolă (F10)

### 5. Metoda Automată - Opțiunea B: MIDI Script (Avansat)

Scriptul `send_kontakt_midi.py` trimite comenzi MIDI la Kontakt:

**Locație:** `scripts_extract\send_kontakt_midi.py`

**Pentru a-l folosi:**
1. Instalează `mido`: `pip install mido`
2. Creează un port MIDI virtual (ex: LoopMIDI)
3. Configurează Kontakt să folosească acel port
4. Rulează: `python send_kontakt_midi.py --port LoopMIDI --pattern Blues`

---

## Setup MIDI (Pentru scripturile automate)

Vezi fișierul: `MIDI_SETUP.md` pentru instrucțiuni completă de configurare MIDI.

---

## Notă Importantă:

Pentru ca scriptul să funcționeze automat, trebuie să ai:
- **Kontakt Script Router** configurat
- Sau un **midi controller** care să trimită note

Dacă nu, rămâne metoda **manuală** (cel mai sigur).

---

## Output:

După ce extragi pattern-urile, le poți folosi în:
- **Magenta** / **LSTM** pentru training
- **Ableton** / **FL Studio** pentru compoziție
- **DAW-ul tău preferat**

---

## Ghid Rapid:

| Pas | Acțiune |
|-----|---------|
| 1 | Deschide REAPER → Add Track |
| 2 | Add FX → Kontakt → Session Guitarist |
| 3 | Arm track (R) |
| 4 | În Kontakt: Pattern → Alege pattern |
| 5 | Record în REAPER |
| 6 | Extract MIDI (Ctrl+E) |
| 7 | Salvează ca `.mid` |

---

**Succes! 🎸**
