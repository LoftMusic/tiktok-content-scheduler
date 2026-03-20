"""
VST Sample Extractor - GUI Version (Modern)
Works with ANY VST plugin via FL Studio
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sounddevice as sd
import numpy as np
import os
import time
from scipy.io import wavfile
import mido
from mido import Message
import threading

# ==================== CONFIG ====================

COLORS = {
    'bg': '#1e1e2e',
    'fg': '#cdd6f4',
    'accent': '#89b4fa',
    'accent_hover': '#b4befe',
    'success': '#a6e3a1',
    'warning': '#f9e2af',
    'error': '#f38ba8',
    'card_bg': '#313244',
    'border': '#45475a'
}

# Note mapping
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_midi(note_str):
    """Convert note string like C4, Cs4, Db4 to MIDI number"""
    note_str = note_str.strip().upper()
    if not note_str:
        return None
    
    note_str = note_str.replace('DB', 'C#').replace('EB', 'D#').replace('GB', 'F#').replace('AB', 'G#').replace('BB', 'A#')
    
    try:
        if len(note_str) >= 2:
            note = note_str[0]
            if note_str[1] in ['#', 'B']:
                note = note_str[0:2]
                octave = int(note_str[2:])
            else:
                octave = int(note_str[1:])
            
            if note in NOTE_NAMES:
                midi = (octave + 1) * 12 + NOTE_NAMES.index(note)
                return midi
    except:
        pass
    
    return None

def midi_to_note_name(midi_num, use_flat=False):
    """Convert MIDI number to note name"""
    octave = (midi_num // 12) - 1
    note = NOTE_NAMES[midi_num % 12]
    
    if use_flat:
        flats = {'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'}
        if note in flats:
            note = flats[note]
    
    return f"{note}{octave}"

def safe_filename(name):
    return name.replace(' ', '_').replace('#', 'b').replace('\\', '').replace('/', '').replace(':', '')

def is_silent(audio, threshold=0.01):
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    return np.max(np.abs(audio)) < threshold

def save_wav(filename, audio, sample_rate):
    max_val = np.max(np.abs(audio))
    if max_val > 0.01:
        audio = audio / max_val * 0.9
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, audio_int16)

# ==================== GUI HELPER FUNCTIONS ====================

def get_midi_ports():
    try:
        return mido.get_output_names()
    except:
        return []

def get_audio_devices():
    devices = []
    try:
        all_devices = sd.query_devices()
        for i, dev in enumerate(all_devices):
            if dev.get('max_input_channels', 0) > 0:
                devices.append(f"{i}: {dev.get('name', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    return devices

# ==================== AUDIO DEVICE SWITCHING ====================

def get_audio_output_devices():
    """Get list of audio output devices using PowerShell"""
    import subprocess
    devices = []
    try:
        # Get audio endpoints
        result = subprocess.run([
            'powershell', '-Command', 
            '''Get-WmiObject Win32_SoundDevice | Where-Object {$_.Name -match "Audio"} | Select-Object -ExpandProperty Name'''
        ], capture_output=True, text=True, timeout=10)
        
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and 'Audio' in line:
                devices.append(line)
    except:
        pass
    return devices

def get_current_audio_device():
    """Get currently active audio output device"""
    import subprocess
    try:
        result = subprocess.run([
            'powershell', '-Command',
            '''Get-AudioDevice -Playback | Select-Object -ExpandProperty Name'''
        ], capture_output=True, text=True, timeout=10)
        if result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    return None

def switch_audio_device(device_name):
    """Switch default audio output device using AudioDeviceCmdlets"""
    import subprocess
    
    # First, get the device index
    ps_command = f'''
$devices = Get-AudioDevice -Playback
$device = $devices | Where-Object {{$_.Name -eq "{device_name}"}}
if ($device) {{
    $device.Index | Set-AudioDevice
    Write-Output "SUCCESS"
}} else {{
    Write-Output "NOT_FOUND"
}}
'''
    try:
        result = subprocess.run(['powershell', '-Command', ps_command], 
                              capture_output=True, text=True, timeout=30)
        return "SUCCESS" in result.stdout
    except Exception as e:
        print(f"Switch error: {e}")
        return False

# ==================== EXTRACTION LOGIC ====================

def run_extraction(config, log_callback, stop_event):
    
    output_dir = config['output_dir']
    midi_port = config['midi_port']
    audio_device = config['audio_device']
    sample_rate = int(config.get('sample_rate', 44100))
    note_duration = float(config.get('note_duration', 0.5))
    velocity = int(config.get('velocity', 100))
    silence_threshold = float(config.get('silence_threshold', 0.01))
    start_note = int(config.get('start_note', 0))
    end_note = int(config.get('end_note', 127))
    naming_pattern = config.get('naming_pattern', '{note}')
    use_flat = config.get('use_flat', False)
    auto_switch_audio = config.get('auto_switch_audio', False)
    target_audio_device = config.get('target_audio_device', '')
    
    original_device = None
    
    # Auto-switch audio device if enabled
    if auto_switch_audio and target_audio_device:
        log_callback("Checking audio device...")
        original_device = get_current_audio_device()
        log_callback(f"Current: {original_device}")
        
        if original_device and target_audio_device.lower() not in original_device.lower():
            log_callback(f"Switching to: {target_audio_device}")
            if switch_audio_device(target_audio_device):
                log_callback("Audio device switched!")
                time.sleep(1)
            else:
                log_callback("Warning: Could not auto-switch audio device")
        else:
            log_callback("Audio device already correct")
    
    os.makedirs(output_dir, exist_ok=True)
    
    notes_to_play = list(range(start_note, end_note + 1))
    note_count = len(notes_to_play)
    
    log_callback("Starting extraction...")
    log_callback(f"Output: {output_dir}")
    log_callback(f"Notes: {start_note} to {end_note} ({note_count} notes)")
    log_callback(f"Pattern: {naming_pattern}")
    log_callback("-" * 40)
    
    # === PHASE 1: Record all notes without checking silence ===
    saved_count = 0
    
    for idx, midi_note in enumerate(notes_to_play):
        if stop_event.is_set():
            log_callback("STOPPED")
            break
        
        note_name = midi_to_note_name(midi_note, use_flat)
        
        filename = naming_pattern.replace('{note}', note_name)
        filename = filename.replace('{midi}', str(midi_note))
        filename = safe_filename(filename) + ".wav"
        
        output_path = os.path.join(output_dir, filename)
        
        log_callback(f"[{idx+1}/{note_count}] {note_name}...")
        
        # Send MIDI
        try:
            with mido.open_output(midi_port) as midi_out:
                midi_out.send(Message('note_on', note=midi_note, velocity=velocity, channel=0))
                time.sleep(note_duration)
                midi_out.send(Message('note_off', note=midi_note, velocity=0, channel=0))
        except Exception as e:
            log_callback(f"  MIDI Error: {e}")
            continue
        
        # Record - save ALL files first
        try:
            recording = sd.rec(int((note_duration + 0.1) * sample_rate),
                            samplerate=sample_rate,
                            channels=2,
                            device=audio_device,
                            dtype='float32')
            sd.wait()
            
            # Save ALL recordings (skip silence check for speed)
            save_wav(output_path, recording, sample_rate)
            saved_count += 1
            log_callback(f"  Saved")
        except Exception as e:
            log_callback(f"  Record Error: {e}")
        
        time.sleep(0.02)  # Shorter delay between notes
    
    log_callback("-" * 40)
    log_callback(f"Recorded {saved_count} files. Checking for silent files...")
    
    # === PHASE 2: Check for silent files and delete them ===
    silent_count = 0
    kept_count = 0
    
    try:
        for filename in os.listdir(output_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(output_dir, filename)
                try:
                    sr, audio = wavfile.read(filepath)
                    audio_float = audio.astype(np.float32) / 32767.0
                    
                    if is_silent(audio_float, silence_threshold):
                        os.remove(filepath)
                        silent_count += 1
                        log_callback(f"  Deleted (silent): {filename}")
                    else:
                        kept_count += 1
                except Exception as e:
                    log_callback(f"  Error checking {filename}: {e}")
    except Exception as e:
        log_callback(f"  Error during cleanup: {e}")
    
    log_callback(f"Silent cleanup: {kept_count} kept, {silent_count} deleted")
    
    # Restore original audio device
    if original_device and auto_switch_audio:
        log_callback("Restoring original audio device...")
        switch_audio_device(original_device)
        log_callback("Done!")
    
    log_callback("=" * 40)
    log_callback("DONE!")

# ==================== GUI CLASS ====================

class VSTExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VST2Wav - Sample Extractor")
        self.root.geometry("780x780")
        self.root.configure(bg=COLORS['bg'])
        self.stop_event = None
        
        # Variables
        self.var_output_dir = tk.StringVar(value=r"C:\Samples\VST_Output")
        self.var_export_name = tk.StringVar(value="MyExport")
        self.var_midi_port = tk.StringVar()
        self.var_audio_device = tk.StringVar()
        self.var_sample_rate = tk.StringVar(value="44100")
        self.var_note_duration = tk.StringVar(value="0.5")
        self.var_velocity = tk.StringVar(value="100")
        self.var_silence_threshold = tk.StringVar(value="0.01")
        
        # Auto audio switch
        self.var_auto_switch = tk.BooleanVar(value=False)
        self.var_target_audio = tk.StringVar()
        
        # Note range variables
        self.var_start_note = tk.StringVar(value="0")
        self.var_end_note = tk.StringVar(value="127")
        self.var_start_type = tk.StringVar(value="midi")
        self.var_end_type = tk.StringVar(value="midi")
        
        # Naming pattern variables
        self.var_naming_pattern = tk.StringVar(value="{note}")
        self.var_naming_type = tk.StringVar(value="note")
        self.var_accidental = tk.StringVar(value="sharp")
        
        self.howto_visible = False
        
        self.create_widgets()
        self.refresh_devices()
        self.refresh_midi()
        
    def create_widgets(self):
        
        # Title
        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(fill=tk.X, pady=15)
        
        title = tk.Label(title_frame, text="VST2Wav", font=("Segoe UI", 28, "bold"), 
                        bg=COLORS['bg'], fg=COLORS['accent'])
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Sample Extractor", font=("Segoe UI", 12),
                          bg=COLORS['bg'], fg=COLORS['fg'])
        subtitle.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # ===== Output Section =====
        self.create_card(main_frame, "Output Settings", 0)
        
        # Export Name
        tk.Label(self.output_card, text="Export Name:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_export_name = tk.Entry(self.output_card, textvariable=self.var_export_name, width=25, bg=COLORS['bg'], fg=COLORS['fg'], 
                insertbackground=COLORS['fg'], relief=tk.FLAT)
        self.entry_export_name.grid(row=0, column=1, padx=10, pady=5)
        
        # Output Folder
        tk.Label(self.output_card, text="Output Folder:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Entry(self.output_card, textvariable=self.var_output_dir, width=25, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.output_card, text="Browse", command=self.browse_output, bg=COLORS['accent'], fg=COLORS['bg'],
                 relief=tk.FLAT, width=8).grid(row=1, column=2, pady=5)
        
        # Auto Audio Switch
        tk.Checkbutton(self.output_card, text="Auto-switch audio output to Virtual Cable", 
                      variable=self.var_auto_switch, bg=COLORS['card_bg'], fg=COLORS['fg'],
                      selectcolor=COLORS['bg']).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        tk.Label(self.output_card, text="Target Device:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.combo_audio_output = ttk.Combobox(self.output_card, textvariable=self.var_target_audio, width=30)
        self.combo_audio_output.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)
        tk.Button(self.output_card, text="Refresh", command=self.refresh_audio_outputs, bg=COLORS['accent'], fg=COLORS['bg'],
                 relief=tk.FLAT, width=8).grid(row=3, column=3, pady=5)
        
        # Naming Pattern
        tk.Label(self.output_card, text="Naming Pattern:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        pattern_frame = tk.Frame(self.output_card, bg=COLORS['card_bg'])
        pattern_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=10, pady=5)
        
        type_toggle = tk.Frame(pattern_frame, bg=COLORS['card_bg'])
        type_toggle.pack(side=tk.LEFT)
        
        self.btn_note = tk.Button(type_toggle, text="Note", command=self.set_naming_type_note,
                     bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN, width=6)
        self.btn_note.pack(side=tk.LEFT, padx=2)
        
        self.btn_midi = tk.Button(type_toggle, text="MIDI #", command=self.set_naming_type_midi,
                     bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED, width=6)
        self.btn_midi.pack(side=tk.LEFT, padx=2)
        
        self.btn_sharp = tk.Button(type_toggle, text="#", command=self.set_accidental_sharp,
                     bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN, width=4)
        self.btn_sharp.pack(side=tk.LEFT, padx=10)
        
        self.btn_flat = tk.Button(type_toggle, text="b", command=self.set_accidental_flat,
                     bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED, width=4)
        self.btn_flat.pack(side=tk.LEFT)
        
        tk.Entry(pattern_frame, textvariable=self.var_naming_pattern, width=15, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        
        # Quick patterns
        quick_pattern = tk.Frame(self.output_card, bg=COLORS['card_bg'])
        quick_pattern.grid(row=5, column=1, columnspan=3, sticky=tk.W, padx=10, pady=2)
        
        for pat in ['{note}', '{note}_{midi}', '{midi}_{note}']:
            tk.Button(quick_pattern, text=pat, command=lambda p=pat: self.var_naming_pattern.set(p),
                     bg=COLORS['bg'], fg=COLORS['accent'], relief=tk.FLAT, width=12).pack(side=tk.LEFT, padx=2)
        
        tk.Label(self.output_card, text="Example: MyExport_C4.wav", bg=COLORS['card_bg'], fg=COLORS['warning'],
                font=("Consolas", 9)).grid(row=6, column=1, sticky=tk.W, padx=10)
        
        # ===== Devices Section =====
        self.create_card(main_frame, "Devices", 1)
        
        # MIDI
        tk.Label(self.devices_card, text="MIDI Output:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_midi = ttk.Combobox(self.devices_card, textvariable=self.var_midi_port, width=30)
        self.combo_midi.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.devices_card, text="Refresh", command=self.refresh_midi, bg=COLORS['accent'], fg=COLORS['bg'],
                 relief=tk.FLAT, width=8).grid(row=0, column=2, pady=5)
        
        # Audio Input
        tk.Label(self.devices_card, text="Audio Input:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_audio = ttk.Combobox(self.devices_card, textvariable=self.var_audio_device, width=30)
        self.combo_audio.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.devices_card, text="Refresh", command=self.refresh_devices, bg=COLORS['accent'], fg=COLORS['bg'],
                 relief=tk.FLAT, width=8).grid(row=1, column=2, pady=5)
        
        # ===== Settings Section =====
        self.create_card(main_frame, "Settings", 2)
        
        # Note Range
        tk.Label(self.settings_card, text="Note Range:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        note_frame = tk.Frame(self.settings_card, bg=COLORS['card_bg'])
        note_frame.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        tk.Entry(note_frame, textvariable=self.var_start_note, width=8, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.btn_start_midi = tk.Button(note_frame, text="MIDI", command=self.set_start_midi,
                     bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN, width=5)
        self.btn_start_midi.pack(side=tk.LEFT, padx=2)
        
        self.btn_start_note = tk.Button(note_frame, text="Note", command=self.set_start_note,
                     bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED, width=5)
        self.btn_start_note.pack(side=tk.LEFT, padx=2)
        
        tk.Label(note_frame, text=" to ", bg=COLORS['card_bg'], fg=COLORS['fg']).pack(side=tk.LEFT, padx=5)
        
        tk.Entry(note_frame, textvariable=self.var_end_note, width=8, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.btn_end_midi = tk.Button(note_frame, text="MIDI", command=self.set_end_midi,
                     bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN, width=5)
        self.btn_end_midi.pack(side=tk.LEFT, padx=2)
        
        self.btn_end_note = tk.Button(note_frame, text="Note", command=self.set_end_note,
                     bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED, width=5)
        self.btn_end_note.pack(side=tk.LEFT, padx=2)
        
        # Quick presets
        quick_frame = tk.Frame(self.settings_card, bg=COLORS['card_bg'])
        quick_frame.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        presets = [
            ("Full", 0, 127),
            ("Piano", 21, 108),
            ("Hi", 60, 84),
            ("Lo", 24, 48),
            ("Bass", 28, 55),
            ("Lead", 48, 72)
        ]
        
        for label, start, end in presets:
            tk.Button(quick_frame, text=label, command=lambda s=start, e=end: [self.var_start_note.set(str(s)), self.var_end_note.set(str(e)), self.set_start_midi(), self.set_end_midi()],
                     bg=COLORS['bg'], fg=COLORS['accent'], relief=tk.FLAT, width=6).pack(side=tk.LEFT, padx=2)
        
        # Other settings
        tk.Label(self.settings_card, text="Duration (s):", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=2, column=0, sticky=tk.W, pady=5)
        tk.Entry(self.settings_card, textvariable=self.var_note_duration, width=10, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        tk.Label(self.settings_card, text="Velocity:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=3, column=0, sticky=tk.W, pady=5)
        tk.Entry(self.settings_card, textvariable=self.var_velocity, width=10, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        tk.Label(self.settings_card, text="Silence Threshold:", bg=COLORS['card_bg'], fg=COLORS['fg']).grid(row=4, column=0, sticky=tk.W, pady=5)
        tk.Entry(self.settings_card, textvariable=self.var_silence_threshold, width=10, bg=COLORS['bg'], fg=COLORS['fg'],
                insertbackground=COLORS['fg'], relief=tk.FLAT).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        # ===== Log Section =====
        log_frame = tk.Frame(main_frame, bg=COLORS['card_bg'], padx=10, pady=10)
        log_frame.grid(row=3, column=0, sticky='nsew', pady=10)
        main_frame.rowconfigure(3, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=65, bg=COLORS['bg'], fg=COLORS['fg'],
                              insertbackground=COLORS['fg'], relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # ===== Buttons =====
        btn_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        btn_frame.grid(row=4, column=0, pady=15)
        
        self.btn_start = tk.Button(btn_frame, text="START EXTRACTION", command=self.start_extraction,
                                   bg=COLORS['success'], fg='#1e1e2e', font=("Segoe UI", 12, "bold"),
                                   relief=tk.RAISED, bd=3, padx=30, pady=12)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop = tk.Button(btn_frame, text="STOP", command=self.stop_extraction,
                                 bg=COLORS['error'], fg='#1e1e2e', font=("Segoe UI", 12, "bold"),
                                 relief=tk.RAISED, bd=3, padx=30, pady=12, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)
        
        self.btn_howto = tk.Button(btn_frame, text="How To Use", command=self.toggle_howto,
                                   bg=COLORS['accent'], fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                                   relief=tk.RAISED, bd=3, padx=20, pady=12)
        self.btn_howto.pack(side=tk.LEFT, padx=20)
        
        # Refresh audio outputs on startup
        self.refresh_audio_outputs()
        
    # ===== TYPE TOGGLE METHODS ====================
    
    def set_naming_type_note(self):
        self.var_naming_type.set("note")
        self.btn_note.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_midi.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_naming_type_midi(self):
        self.var_naming_type.set("midi")
        self.btn_midi.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_note.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_accidental_sharp(self):
        self.var_accidental.set("sharp")
        self.btn_sharp.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_flat.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_accidental_flat(self):
        self.var_accidental.set("flat")
        self.btn_flat.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_sharp.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_start_midi(self):
        self.var_start_type.set("midi")
        self.btn_start_midi.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_start_note.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_start_note(self):
        self.var_start_type.set("note")
        self.btn_start_note.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_start_midi.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_end_midi(self):
        self.var_end_type.set("midi")
        self.btn_end_midi.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_end_note.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    def set_end_note(self):
        self.var_end_type.set("note")
        self.btn_end_note.config(bg=COLORS['accent'], fg=COLORS['bg'], relief=tk.SUNKEN)
        self.btn_end_midi.config(bg=COLORS['bg'], fg=COLORS['fg'], relief=tk.RAISED)
        
    # ===== OTHER METHODS ====================
        
    def create_card(self, parent, title, row):
        card = tk.LabelFrame(parent, text=title, bg=COLORS['card_bg'], fg=COLORS['fg'],
                           font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        card.grid(row=row, column=0, sticky='ew', pady=5)
        parent.columnconfigure(0, weight=1)
        
        if "Output" in title:
            self.output_card = card
        elif "Devices" in title:
            self.devices_card = card
        elif "Settings" in title:
            self.settings_card = card
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder", initialdir=self.var_output_dir.get())
        if folder:
            self.var_output_dir.set(folder)
            self.entry_export_name.focus_set()
            self.entry_export_name.select_range(0, tk.END)
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def toggle_howto(self):
        if self.howto_visible:
            try:
                self.howto_window.withdraw()
            except:
                pass
            self.btn_howto.config(text="How To Use")
            self.howto_visible = False
        else:
            self.show_howto_window()
            self.btn_howto.config(text="Hide How To")
            self.howto_visible = True
            
    def show_howto_window(self):
        self.howto_window = tk.Toplevel(self.root)
        self.howto_window.title("How To Use")
        self.howto_window.geometry("540x540")
        self.howto_window.configure(bg=COLORS['bg'])
        
        text = tk.Text(self.howto_window, bg=COLORS['card_bg'], fg=COLORS['fg'], 
                      font=("Consolas", 10), padx=20, pady=20, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        
        howto = """VST2Wav - How To Use
===============================


PREREQUISITES:
1. Download & install loopMIDI:
   https://www.tobias-errichsen.de/software/loopmidi.html

2. Virtual Audio Cable (already installed)

3. FL Studio (or any DAW)


SETUP:
1. Run loopMIDI and create a port

2. In FL Studio:
   - Add your VST plugin
   - Audio Output: Virtual Audio Cable
   - Enable MIDI Input: loopMIDI port

3. In this app:
   - Select MIDI Output: loopMIDI Port
   - Select Audio Input: Virtual Audio Cable


AUTO AUDIO SWITCH (Optional):
- Enable "Auto-switch audio output"
- Select target device (e.g., "Virtual Audio Cable")
- App will switch audio during extraction
- Automatically reverts when done


NOTE RANGE:
You can input as MIDI numbers or Note names:

MIDI: 0-127
Notes: C-1 to G8 (or C1-C8)

Examples:
  MIDI: 0 to 127 (full range)
  Note: C1 to C6 (piano range)


NAMING PATTERN:
Toggle between Note or MIDI#:

Note mode: {note} = C4, Cs4, Db4
MIDI mode: {midi} = 60, 61, 62

Accidental toggle (# or b):
  # = C#4, D#4
  b = Db4, Eb4


QUICK PRESETS:
Click preset buttons for common ranges:
Full, Piano, Hi, Lo, Bass, Lead


START:
Click START and watch the extraction!
Silent notes are automatically deleted.
"""
        text.insert(1.0, howto)
        text.config(state=tk.DISABLED)
        
    def refresh_midi(self):
        ports = get_midi_ports()
        self.combo_midi['values'] = ports
        if ports:
            for p in ports:
                if 'loop' in p.lower():
                    self.var_midi_port.set(p)
                    return
            self.var_midi_port.set(ports[0])
                
    def refresh_devices(self):
        devices = get_audio_devices()
        self.combo_audio['values'] = devices
        if devices:
            for d in devices:
                if 'virtual' in d.lower() or 'cable' in d.lower():
                    self.var_audio_device.set(d)
                    return
            self.var_audio_device.set(devices[0])
    
    def refresh_audio_outputs(self):
        """Refresh audio output devices for auto-switch"""
        devices = get_audio_output_devices()
        self.combo_audio_output['values'] = devices
        if devices:
            # Try to find Virtual Audio Cable
            for d in devices:
                if 'virtual' in d.lower() or 'cable' in d.lower():
                    self.var_target_audio.set(d)
                    return
            self.var_target_audio.set(devices[0])
                
    def get_audio_device_number(self):
        dev_str = self.var_audio_device.get()
        if ':' in dev_str:
            return int(dev_str.split(':')[0].strip())
        try:
            return int(dev_str)
        except:
            return 1
    
    def convert_note_range(self):
        start = self.var_start_note.get()
        end = self.var_end_note.get()
        
        if self.var_start_type.get() == "note":
            midi = note_to_midi(start)
            if midi is not None:
                start = str(midi)
        
        if self.var_end_type.get() == "note":
            midi = note_to_midi(end)
            if midi is not None:
                end = str(midi)
        
        return int(start), int(end)
    
    def get_naming_pattern(self):
        base = self.var_export_name.get()
        
        if self.var_naming_type.get() == "midi":
            pattern = base + "_{midi}"
        else:
            pattern = base + "_{note}"
        
        return pattern
            
    def start_extraction(self):
        if not self.var_midi_port.get():
            messagebox.showerror("Error", "Please select MIDI output")
            return
        if not self.var_audio_device.get():
            messagebox.showerror("Error", "Please select audio input")
            return
        if not self.var_output_dir.get():
            messagebox.showerror("Error", "Please select output folder")
            return
        
        # Check auto-switch requirements
        if self.var_auto_switch.get() and not self.var_target_audio.get():
            messagebox.showerror("Error", "Please select target audio device for auto-switch")
            return
        
        try:
            start_note, end_note = self.convert_note_range()
        except:
            messagebox.showerror("Error", "Invalid note range")
            return
        
        config = {
            'output_dir': self.var_output_dir.get(),
            'midi_port': self.var_midi_port.get(),
            'audio_device': self.get_audio_device_number(),
            'sample_rate': self.var_sample_rate.get(),
            'note_duration': self.var_note_duration.get(),
            'velocity': self.var_velocity.get(),
            'silence_threshold': self.var_silence_threshold.get(),
            'start_note': str(start_note),
            'end_note': str(end_note),
            'naming_pattern': self.get_naming_pattern(),
            'use_flat': self.var_accidental.get() == "flat",
            'auto_switch_audio': self.var_auto_switch.get(),
            'target_audio_device': self.var_target_audio.get()
        }
        
        self.stop_event = threading.Event()
        self.btn_start.config(state=tk.DISABLED, bg=COLORS['warning'])
        self.btn_stop.config(state=tk.NORMAL, bg=COLORS['error'])
        
        thread = threading.Thread(target=self.run_extraction_thread, args=(config,))
        thread.start()
        
    def run_extraction_thread(self, config):
        try:
            run_extraction(config, self.log, self.stop_event)
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.root.after(0, self.extraction_done)
            
    def extraction_done(self):
        self.btn_start.config(state=tk.NORMAL, bg=COLORS['success'])
        self.btn_stop.config(state=tk.DISABLED)
        messagebox.showinfo("Done", "Extraction complete!")
        
    def stop_extraction(self):
        if self.stop_event:
            self.stop_event.set()
            self.log("Stopping...")

# ==================== MAIN ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = VSTExtractorGUI(root)
    root.mainloop()
