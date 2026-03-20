#!/usr/bin/env python3
"""
Audio Recorder for Windows - Splice Samples
Captures system audio, removes silence, saves to organized folders
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os
import time
from pathlib import Path
from datetime import datetime

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = None
        self.sample_rate = 44100
        self.channels = 2
        self.output_dir = Path.home() / "Audio" / "splice_samples"
        self.device = None
        self.last_file = None
        
    def get_input_devices(self):
        """Get all input devices"""
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_input_channels'] > 0:
                devices.append((i, dev['name'], dev['max_input_channels']))
        return devices
    
    def set_device(self, device_id):
        """Set the input device"""
        self.device = device_id
        print(f"Device set to: {device_id} - {sd.query_devices(device_id)['name']}")
        
    def record(self, max_duration=30):
        """Record audio from selected device"""
        if self.recording:
            return None
            
        self.recording = True
        self.audio_data = None
        
        def record_thread():
            try:
                device = self.device
                if device is None:
                    # Try to find Virtual Audio Cable or loopback
                    devices = self.get_input_devices()
                    for idx, name, chans in devices:
                        if 'virtual' in name.lower() or 'cable' in name.lower() or 'line' in name.lower():
                            device = idx
                            print(f"Auto-selected: {name}")
                            break
                    
                    if device is None:
                        print("Using default input device")
                        device = sd.query_devices(kind='input')['index']
                
                device_info = sd.query_devices(device)
                print(f"Recording from: {device_info['name']}")
                print(f"Input channels: {device_info['max_input_channels']}")
                
                # Use device's default sample rate or fallback to 44100
                self.sample_rate = int(device_info.get('default_samplerate', 44100))
                self.channels = min(2, device_info['max_input_channels'])
                
                recording = sd.rec(
                    int(max_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    device=device,
                    dtype='float32'
                )
                
                print(f"Recording started... (max {max_duration}s)")
                
                sd.wait()
                self.audio_data = recording
                print(f"Recording finished: {len(recording)} samples")
                
            except Exception as e:
                print(f"Recording error: {e}")
                import traceback
                traceback.print_exc()
                self.audio_data = None
            finally:
                self.recording = False
        
        thread = threading.Thread(target=record_thread)
        thread.start()
        return thread
        
    def stop(self):
        """Stop recording"""
        self.recording = False
        sd.stop()
        
    def trim_silence(self, audio, threshold_db=-40):
        """Remove silence from beginning and end"""
        if audio is None or len(audio) == 0:
            return None
        
        # Convert dB to amplitude
        threshold = 10 ** (threshold_db / 20)
        
        # Get amplitude (max of channels)
        if len(audio.shape) > 1:
            amplitude = np.max(np.abs(audio), axis=1)
        else:
            amplitude = np.abs(audio)
        
        # Find non-silent regions
        non_silent = amplitude > threshold
        
        if not np.any(non_silent):
            print("No audio detected (all silence)")
            return None
        
        # Find start and end
        indices = np.where(non_silent)[0]
        start = max(0, indices[0] - 100)  # 100 samples padding
        end = min(len(audio) - 1, indices[-1] + 100)
        
        trimmed = audio[start:end + 1]
        
        duration = len(trimmed) / self.sample_rate
        print(f"Trimmed: {duration:.3f}s ({len(trimmed)} samples)")
        
        return trimmed
    
    def save(self, audio, filename=None, category=None):
        """Save audio to file"""
        if audio is None:
            return None
        
        # Create output directory
        if category:
            save_dir = self.output_dir / category
        else:
            save_dir = self.output_dir
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sample_{timestamp}"
        
        if not filename.endswith(('.wav', '.flac')):
            filename += '.wav'
        
        filepath = save_dir / filename
        
        # Handle duplicate filenames
        counter = 1
        while filepath.exists():
            stem = filepath.stem
            filepath = save_dir / f"{stem}_{counter}.wav"
            counter += 1
        
        # Save
        sf.write(str(filepath), audio, self.sample_rate)
        print(f"Saved: {filepath}")
        
        return filepath


class RecorderGUI:
    def __init__(self):
        self.recorder = AudioRecorder()
        
        self.root = tk.Tk()
        self.root.title("Audio Recorder")
        self.root.geometry("450x600")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        self.categories = ['kick', 'snare', 'hihat', 'tom', 'clap', 'perc', 'loop', 'fx', 'vocal', 'other']
        self.current_category = tk.StringVar(value='kick')
        self.recording = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Segoe UI', 10))
        style.configure('TLabelframe', background='#1a1a2e', foreground='white')
        style.configure('TLabelframe.Label', background='#1a1a2e', foreground='white', font=('Segoe UI', 10, 'bold'))
        
        # Main container
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main, text="🎵 Splice Sample Recorder", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 15))
        
        # === DEVICE SELECTION ===
        device_frame = ttk.LabelFrame(main, text="Input Device", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, state='readonly', width=40)
        self.device_combo.pack(fill=tk.X)
        
        # Populate devices
        devices = self.recorder.get_input_devices()
        device_names = [f"{idx}: {name}" for idx, name, chans in devices]
        self.device_combo['values'] = device_names
        self.device_combo.current(0)
        
        ttk.Button(device_frame, text="🔄 Refresh Devices", command=self.refresh_devices).pack(pady=(5, 0))
        
        # === CATEGORY ===
        cat_frame = ttk.LabelFrame(main, text="Category", padding=10)
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        cat_buttons = ttk.Frame(cat_frame)
        cat_buttons.pack(fill=tk.X)
        
        for i, cat in enumerate(self.categories):
            btn = tk.Button(
                cat_buttons,
                text=cat.upper(),
                font=('Segoe UI', 9),
                bg='#4a4a6a' if cat != 'kick' else '#6b46c1',
                fg='white',
                activebackground='#6b46c1',
                activeforeground='white',
                relief='flat',
                padx=8,
                pady=4,
                command=lambda c=cat: self.set_category(c)
            )
            btn.grid(row=i//5, column=i%5, padx=2, pady=2, sticky='ew')
            cat_buttons.columnconfigure(i%5, weight=1)
        
        self.category_label = ttk.Label(cat_frame, text="Selected: KICK", font=('Segoe UI', 10, 'bold'))
        self.category_label.pack(pady=(10, 0))
        
        # === FILENAME ===
        name_frame = ttk.LabelFrame(main, text="Filename (optional)", padding=10)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filename_entry = ttk.Entry(name_frame, width=40)
        self.filename_entry.pack(fill=tk.X)
        self.filename_entry.insert(0, "")
        
        # === RECORD BUTTON ===
        record_frame = ttk.Frame(main)
        record_frame.pack(fill=tk.X, pady=15)
        
        self.record_btn = tk.Button(
            record_frame,
            text="⏺  RECORD",
            font=('Segoe UI', 16, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            width=20,
            height=2,
            command=self.toggle_record
        )
        self.record_btn.pack()
        
        # === STATUS ===
        self.status_var = tk.StringVar(value="Ready - Select device and category, then record")
        self.status_label = ttk.Label(main, textvariable=self.status_var, font=('Segoe UI', 9), wraplength=400)
        self.status_label.pack(pady=10)
        
        # === ACTIONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="▶ Play Last", command=self.play_last).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📁 Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=5)
        
        # === SETTINGS ===
        settings_frame = ttk.LabelFrame(main, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(settings_frame, text="Silence Threshold (dB):").pack(anchor='w')
        self.threshold_var = tk.IntVar(value=-40)
        threshold_scale = ttk.Scale(settings_frame, from_=-60, to=-20, variable=self.threshold_var, orient='horizontal')
        threshold_scale.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text=f"Output: {self.recorder.output_dir}", font=('Segoe UI', 8)).pack(anchor='w', pady=(10, 0))
        
    def set_category(self, category):
        self.current_category.set(category)
        self.category_label.config(text=f"Selected: {category.upper()}")
        
        # Update button colors
        for widget in self.root.winfo_children():
            pass  # Could update button colors here
        
    def refresh_devices(self):
        devices = self.recorder.get_input_devices()
        device_names = [f"{idx}: {name}" for idx, name, chans in devices]
        self.device_combo['values'] = device_names
        if device_names:
            self.device_combo.current(0)
        self.status_var.set("Devices refreshed")
        
    def toggle_record(self):
        if not self.recording:
            # Start recording
            device_str = self.device_var.get()
            if device_str:
                device_id = int(device_str.split(':')[0])
                self.recorder.set_device(device_id)
            
            self.recording = True
            self.record_btn.config(text="⏹  STOP", bg='#f39c12')
            self.status_var.set("🔴 Recording... Play your sample now!")
            
            self.recorder.record(max_duration=30)
            self.root.after(100, self.check_recording)
        else:
            # Stop recording
            self.recorder.stop()
            self.finish_recording()
            
    def check_recording(self):
        if self.recorder.recording:
            self.root.after(100, self.check_recording)
        else:
            self.finish_recording()
            
    def finish_recording(self):
        self.recording = False
        self.record_btn.config(text="⏺  RECORD", bg='#e74c3c')
        
        if self.recorder.audio_data is None:
            self.status_var.set("❌ No audio recorded")
            return
        
        self.status_var.set("Processing...")
        self.root.update()
        
        # Trim silence
        threshold = self.threshold_var.get()
        trimmed = self.recorder.trim_silence(self.recorder.audio_data, threshold)
        
        if trimmed is None or len(trimmed) < 100:
            self.status_var.set("❌ No audio detected (too quiet or empty)")
            return
        
        # Get filename
        filename = self.filename_entry.get().strip() or None
        
        # Save
        category = self.current_category.get()
        filepath = self.recorder.save(trimmed, filename, category)
        
        if filepath:
            self.recorder.last_file = filepath
            duration = len(trimmed) / self.recorder.sample_rate
            self.status_var.set(f"✅ Saved: {filepath.name} ({duration:.2f}s)")
            self.filename_entry.delete(0, tk.END)
        else:
            self.status_var.set("❌ Save failed")
            
    def play_last(self):
        if not self.recorder.last_file or not self.recorder.last_file.exists():
            messagebox.showinfo("Play", "No recording yet")
            return
        
        try:
            data, sr = sf.read(str(self.recorder.last_file))
            sd.play(data, sr)
            self.status_var.set(f"▶ Playing: {self.recorder.last_file.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play: {e}")
            
    def open_folder(self):
        import subprocess
        folder = self.recorder.output_dir
        folder.mkdir(parents=True, exist_ok=True)
        os.startfile(str(folder))
        
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    print("=" * 50)
    print("Audio Recorder for Splice Samples")
    print("=" * 50)
    print("\nUsage:")
    print("1. Set Virtual Audio Cable as your browser output")
    print("2. Select 'Line 1 (Virtual Audio Cable)' as input device")
    print("3. Choose a category (kick, snare, etc.)")
    print("4. Click RECORD, play sample in browser, then STOP")
    print("5. Audio is automatically trimmed and saved")
    print("=" * 50)
    
    try:
        app = RecorderGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")