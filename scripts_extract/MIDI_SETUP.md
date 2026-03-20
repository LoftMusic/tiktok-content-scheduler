# Setup MIDI pentru Session Guitarist (Opțional)

## Pentru a folosi `send_kontakt_midi.py`

### Pas 1: Instalează依赖

```bash
pip install mido
pip install pywin32  # doar pentru Windows
```

### Pas 2: Creează un port MIDI virtual

#### Opțiunea A: LoopMIDI (recomandat)
1. Descarcă de la: https://www.tobias-erichsen.de/software/loopmidi.html
2. Instalează și rulează
3. Dă click pe `+` pentru a crea un port nou
4. Dă nume portului (ex: "Kontakt MIDI In")

#### Opțiunea B: VirtualMIDISynth (alternativ)
1. Descarcă de la: https://coolsoft.altervista.org/en/virtualmidisynth
2. Instalează și configurează
3. Portul va apărea ca "Virtual MIDI Synth"

### Pas 3: Configurează Kontakt

1. Deschide Kontakt
2. Mergi la `Preferences` → `Audio & MIDI`
3. În secțiunea **MIDI Input**, activează portul creat
4. Asigură-te că `MIDI In` este setat pe portul tău

### Pas 4: Configurează REAPER (dacă folosești și asta)

1. În REAPER, mergi la `Options` → `Preferences` → `Audio` → `MIDI Devices`
2. Activează portul tău în **MIDI Input**

### Pas 5: Testează

Rulează scriptul de test:

```bash
python send_kontakt_midi.py --list-ports
python send_kontakt_midi.py --port "LoopMIDI" --pattern Blues
```

---

## Comenzi Disponibile

| Comandă | Descriere |
|---------|-----------|
| `--list-ports` | Listă porturi MIDI disponibile |
| `--list` | Listă pattern-uri disponibile |
| `--port LoopMIDI --pattern Blues` | Trimite pattern-ul "Blues" |
| `--port LoopMIDI --all` | Trimite toate pattern-urile |

---

## Notă:

Scriptul `send_kontakt_midi.py` trimite **note MIDI** la Kontakt pentru a selecta pattern-urile.

**Nu este o metodă oficială NI**, așa că poate funcționa diferit în funcție de versiunea ta de Kontakt.

Dacă nu funcționează, folosește metoda **manuală** sau **ReaScript**.