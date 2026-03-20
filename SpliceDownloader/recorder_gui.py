"""
Auto-Switch Sample Recorder - GUI
Automatically switches to VAC for recording, then restores original output
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os
import sounddevice as sd
import numpy as np
from scipy.io import wavfile

# Configuration
SAMPLE_RATE = 44100
CHANNELS = 2
SILENCE_THRESHOLD = 0.02

class RecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Switch Sample Recorder")
        self.root.geometry("550x720")
        self.root.resizable(True, True)

        self.recording = False
        self.stream = None

        self.setup_ui()
        self.refresh_devices()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Auto-Switch Sample Recorder",
                       font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)

        # Current output frame
        output_frame = ttk.LabelFrame(self.root, text="Current Output Device")
        output_frame.pack(fill="x", padx=20, pady=5)

        self.output_label = tk.Label(output_frame, text="Loading...",
                                     font=("Segoe UI", 10))
        self.output_label.pack(pady=10)

        # VAC status frame
        vac_frame = ttk.LabelFrame(self.root, text="VAC Status")
        vac_frame.pack(fill="x", padx=20, pady=5)

        self.vac_status = tk.Label(vac_frame, text="Checking...",
                                   font=("Segoe UI", 10))
        self.vac_status.pack(pady=10)

        # Recording mode frame
        mode_frame = ttk.LabelFrame(self.root, text="Recording Mode")
        mode_frame.pack(fill="x", padx=20, pady=5)

        self.mode_var = tk.StringVar(value="manual")

        rb1 = ttk.Radiobutton(mode_frame, text="Manual (press Enter to stop)",
                              variable=self.mode_var, value="manual",
                              command=self.toggle_duration)
        rb1.pack(anchor="w", padx=10, pady=2)

        rb2 = ttk.Radiobutton(mode_frame, text="Timed",
                              variable=self.mode_var, value="timed",
                              command=self.toggle_duration)
        rb2.pack(anchor="w", padx=10, pady=2)

        duration_frame = ttk.Frame(mode_frame)
        duration_frame.pack(anchor="w", padx=10, pady=5)

        tk.Label(duration_frame, text="Duration (seconds):").pack(side="left")
        self.duration_entry = ttk.Entry(duration_frame, width=10, state="disabled")
        self.duration_entry.insert(0, "10")
        self.duration_entry.pack(side="left", padx=5)

        # Silence removal frame
        trim_frame = ttk.LabelFrame(self.root, text="Silence Removal")
        trim_frame.pack(fill="x", padx=20, pady=5)

        self.trim_var = tk.BooleanVar(value=True)
        self.trim_checkbox = ttk.Checkbutton(trim_frame, text="Remove silence from samples",
                                             variable=self.trim_var)
        self.trim_checkbox.pack(anchor="w", padx=10, pady=2)

        threshold_frame = ttk.Frame(trim_frame)
        threshold_frame.pack(anchor="w", padx=10, pady=2)

        tk.Label(threshold_frame, text="Threshold:").pack(side="left")
        self.threshold_entry = ttk.Entry(threshold_frame, width=8)
        self.threshold_entry.insert(0, "0.005")
        self.threshold_entry.pack(side="left", padx=5)

        # Fade-out setting
        fade_frame = ttk.Frame(trim_frame)
        fade_frame.pack(anchor="w", padx=10, pady=2)

        tk.Label(fade_frame, text="Fade-out (ms):").pack(side="left")
        self.fade_entry = ttk.Entry(fade_frame, width=8)
        self.fade_entry.insert(0, "20")
        self.fade_entry.pack(side="left", padx=5)

        # Min gap setting for slice detection
        gap_frame = ttk.Frame(trim_frame)
        gap_frame.pack(anchor="w", padx=10, pady=2)

        tk.Label(gap_frame, text="Min Gap (ms):").pack(side="left")
        self.gap_entry = ttk.Entry(gap_frame, width=8)
        self.gap_entry.insert(0, "150")
        self.gap_entry.pack(side="left", padx=5)
        tk.Label(gap_frame, text="(for slicing samples)", font=("Segoe UI", 8)).pack(side="left")

        # Loop mode checkbox
        self.loop_var = tk.BooleanVar(value=False)
        self.loop_checkbox = ttk.Checkbutton(trim_frame, text="Loop Mode (trim only start/end, keep internal gaps)",
                                              variable=self.loop_var)
        self.loop_checkbox.pack(anchor="w", padx=10, pady=2)

        # Category selection frame
        cat_frame = ttk.LabelFrame(self.root, text="Sample Category")
        cat_frame.pack(fill="x", padx=20, pady=5)

        self.base_path = r"G:\ASU STUDIO SAMPLES\SAMPLES ASU\SAMPLES 2026\Trase"
        
        self.categories = ["Kick", "Snare", "HiHat", "Clap", "Perc", "FX", "Vocal", "Bass", "Melody", "Loop", "Other"]
        self.category_var = tk.StringVar(value="Kick")
        
        cat_combo_frame = ttk.Frame(cat_frame)
        cat_combo_frame.pack(anchor="w", padx=10, pady=5)
        
        tk.Label(cat_combo_frame, text="Category:").pack(side="left")
        self.category_combo = ttk.Combobox(cat_combo_frame, textvariable=self.category_var, 
                                            values=self.categories, state="readonly", width=15)
        self.category_combo.pack(side="left", padx=5)

        # Status
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.status_label = tk.Label(status_frame, text="Ready",
                                     font=("Segoe UI", 11, "bold"),
                                     fg="green")
        self.status_label.pack()

        # Record button
        self.record_btn = ttk.Button(self.root, text="START RECORDING",
                                     command=self.toggle_recording,
                                     style="Accent.TButton")
        self.record_btn.pack(pady=10)

        # Configure ttk style for button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"))

    def toggle_duration(self):
        if self.mode_var.get() == "timed":
            self.duration_entry.config(state="normal")
        else:
            self.duration_entry.config(state="disabled")

    def refresh_devices(self):
        """Check current output device and VAC status"""
        try:
            # Get actual default devices from sounddevice
            try:
                default_output = sd.query_devices(kind="output")
                output_name = default_output.get("name", "Unknown")
                self.output_label.config(text=output_name, fg="blue")
            except Exception as e:
                self.output_label.config(text="No default output", fg="gray")

            # Check default input (should be VAC for recording)
            try:
                default_input = sd.query_devices(kind="input")
                input_name = default_input.get("name", "Unknown")

                if "Virtual Audio Cable" in input_name:
                    self.vac_status.config(text=f"✓ VAC as input: {input_name}", fg="green")
                else:
                    self.vac_status.config(text=f"⚠ Input: {input_name} (not VAC!)", fg="orange")
            except:
                self.vac_status.config(text="✗ No default input", fg="red")

        except Exception as e:
            self.output_label.config(text=f"Error: {str(e)}", fg="red")

    def get_vac_device_id(self):
        """Get VAC device ID from registry"""
        try:
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command',
                 "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Multimedia\\Sound Mapper' -Name 'Playback' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Playback"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        except:
            return None

    def switch_to_vac(self):
        """Switch output AND input to Virtual Audio Cable using AudioDeviceCmdlets"""

        # First get current devices BEFORE switching
        orig_out, orig_in = self.get_current_devices()
        print(f"Before switch - Output: {orig_out}, Input: {orig_in}")

        # PowerShell script that switches devices
        script = """
Import-Module AudioDeviceCmdlets

# Switch playback to VAC (Index 2)
Set-AudioDevice -Index 2

# Switch recording to VAC (Index 5)
Get-AudioDevice -List | Where-Object { $_.Index -eq 5 } | Set-AudioDevice

Start-Sleep -Milliseconds 500
"""

        try:
            subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
                capture_output=True, text=True, timeout=15
            )
            print(f"Switched to VAC!")
            return [orig_out, orig_in]

        except Exception as e:
            print(f"Error switching to VAC: {e}")
            return [None, None]

    def restore_output(self, original_output, original_input):
        """Restore original output and input devices"""
        print(f"Restoring - Output: {original_output}, Input: {original_input}")

        if not original_output or not original_input:
            print("No original devices to restore")
            return

        script = f"""
Import-Module AudioDeviceCmdlets

# Find devices by ID and restore
Get-AudioDevice -List | Where-Object {{ $_.ID -eq "{original_output}" }} | Set-AudioDevice
Start-Sleep -Milliseconds 200
Get-AudioDevice -List | Where-Object {{ $_.ID -eq "{original_input}" }} | Set-AudioDevice

Start-Sleep -Milliseconds 500
"""

        try:
            subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
                capture_output=True, text=True, timeout=15
            )
            print("Devices restored!")
        except Exception as e:
            print(f"Error restoring output: {e}")

    def get_current_devices(self):
        """Get current output and input device IDs"""
        script = """
Import-Module AudioDeviceCmdlets
$p = Get-AudioDevice -Playback
$r = Get-AudioDevice -Recording
Write-Output "OUTPUT:$($p.ID)"
Write-Output "INPUT:$r.ID"
"""
        try:
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
                capture_output=True, text=True, timeout=10
            )
            output = result.stdout
            output_id = None
            input_id = None

            for line in output.split('\n'):
                if line.startswith('OUTPUT:'):
                    output_id = line.replace('OUTPUT:', '').strip()
                elif line.startswith('INPUT:'):
                    input_id = line.replace('INPUT:', '').strip()

            return [output_id, input_id]
        except Exception as e:
            print(f"Error getting devices: {e}")
            return [None, None]

    def start_recording(self):
        """Start recording in a separate thread"""
        self.recording = True
        self.record_btn.config(text="STOP RECORDING")
        self.status_label.config(text="Saving original devices...", fg="orange")
        self.root.update()

        # Switch BOTH output and input to VAC
        self.original_output, self.original_input = self.switch_to_vac()
        self.refresh_devices()

        # Small delay to let audio switch settle
        time.sleep(0.5)

        # Start recording thread
        threading.Thread(target=self.record_audio, daemon=True).start()

    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        self.status_label.config(text="Finishing recording...", fg="orange")
        self.root.update()
        
        # Wait 50ms to capture the tail
        time.sleep(0.05)
        
        self.record_btn.config(text="START RECORDING")
        self.status_label.config(text="Stopping and restoring devices...", fg="orange")

        # Restore original output and input
        self.restore_output(self.original_output, self.original_input)

        self.refresh_devices()
        self.status_label.config(text="Done! Devices restored to original.", fg="green")

    def toggle_recording(self):
        """Toggle recording state"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def record_audio(self):
        """Record audio using sounddevice"""
        try:
            # Re-query default input after switching to VAC
            time.sleep(0.3)
            default_input = sd.query_devices(kind='input')
            input_name = default_input.get('name', '')

            self.root.after(0, lambda: self.status_label.config(
                text=f"Recording from: {input_name[:30]}...", fg="red"))

            if self.mode_var.get() == "timed":
                try:
                    duration = int(self.duration_entry.get())
                except:
                    duration = 10

                self.root.after(0, lambda: self.status_label.config(
                    text=f"Recording for {duration}s...", fg="red"))

                recording = sd.rec(
                    int(duration * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype='float32'
                )
                sd.wait()

            else:
                # Manual recording - record continuously without gaps
                self.root.after(0, lambda: self.status_label.config(
                    text="Recording... (press STOP)", fg="red"))
                self.root.update()

                # Use a single continuous recording buffer
                chunks = []
                chunk_size = int(1 * SAMPLE_RATE)  # 1 second chunks
                
                while self.recording:
                    chunk = sd.rec(chunk_size, samplerate=SAMPLE_RATE,
                                   channels=CHANNELS, dtype='float32')
                    sd.wait()  # Wait for chunk to complete
                    chunks.append(chunk.copy())  # Copy to avoid overwrite
                    self.root.update()  # Keep UI responsive

                if chunks:
                    recording = np.concatenate(chunks, axis=0)
                else:
                    recording = np.array([])

            # Check if there's audio
            if len(recording) > 0:
                max_vol = np.max(np.abs(recording))

                max_vol = np.max(np.abs(recording))

                if max_vol > 0.001:
                    # Check if silence removal is enabled
                    do_trim = self.trim_var.get()

                    if do_trim:
                        try:
                            threshold = float(self.threshold_entry.get())
                            fade_ms = int(self.fade_entry.get())
                            gap_ms = int(self.gap_entry.get())
                            loop_mode = self.loop_var.get()
                        except:
                            threshold = 0.005
                            fade_ms = 20
                            gap_ms = 150
                            loop_mode = False

                        mode_text = "Loop mode: trimming edges..." if loop_mode else "Processing: Removing silence..."
                        self.root.after(0, lambda mt=mode_text: self.status_label.config(text=mt, fg="orange"))
                        self.root.update()

                        # Debug: print settings
                        print(f"Settings: threshold={threshold}, gap_ms={gap_ms}, loop_mode={loop_mode}")
                        print(f"Recording length: {len(recording)/SAMPLE_RATE:.2f}s, max_vol={max_vol:.4f}")

                        segments = self.remove_silence(recording, threshold, fade_ms, gap_ms, loop_mode)
                        print(f"Found {len(segments)} segment(s)")

                        if segments:
                            if loop_mode:
                                # Loop mode: single file with trimmed start/end
                                self.root.after(0, lambda: self.status_label.config(
                                    text="Choose save location...", fg="orange"))
                                filename = filedialog.asksaveasfilename(
                                    defaultextension=".wav",
                                    filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                                    title="Save Loop Recording"
                                )
                                if filename:
                                    wavfile.write(filename, SAMPLE_RATE, (segments[0] * 32767).astype(np.int16))
                                    self.root.after(0, lambda f=filename: self.status_label.config(
                                        text=f"Saved: {os.path.basename(f)}", fg="green"))
                                else:
                                    self.root.after(0, lambda: self.status_label.config(
                                        text="Save cancelled", fg="orange"))
                            else:
                                # Normal mode: save to category folder
                                category = self.category_var.get()
                                
                                # Loop category: prompt for name and save to Loop folder
                                if category == "Loop":
                                    save_dir = os.path.join(self.base_path, "Loop")
                                    os.makedirs(save_dir, exist_ok=True)
                                    
                                    self.root.after(0, lambda: self.status_label.config(
                                        text="Enter loop name...", fg="orange"))
                                    self.root.update()
                                    
                                    filename = filedialog.asksaveasfilename(
                                        defaultextension=".wav",
                                        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                                        initialdir=save_dir,
                                        title="Save Loop"
                                    )
                                    if filename:
                                        # Make sure it ends with .wav
                                        if not filename.lower().endswith('.wav'):
                                            filename += '.wav'
                                        wavfile.write(filename, SAMPLE_RATE, (segments[0] * 32767).astype(np.int16))
                                        self.root.after(0, lambda f=filename: self.status_label.config(
                                            text=f"Saved: {os.path.basename(f)}", fg="green"))
                                    else:
                                        self.root.after(0, lambda: self.status_label.config(
                                            text="Save cancelled", fg="orange"))
                                else:
                                    # Other categories: auto-numbering
                                    save_dir = os.path.join(self.base_path, category)
                                    
                                    # Create folder if doesn't exist
                                    os.makedirs(save_dir, exist_ok=True)
                                    
                                    # Find next available number
                                    existing = [f for f in os.listdir(save_dir) if f.startswith(category) and f.endswith('.wav')]
                                    next_num = len(existing) + 1
                                    
                                    # Find first available number
                                    used_nums = set()
                                    for f in existing:
                                        try:
                                            num = int(f.replace(category, '').replace('.wav', '').strip().replace('_', ''))
                                            used_nums.add(num)
                                        except:
                                            pass
                                    
                                    while next_num in used_nums:
                                        next_num += 1
                                    
                                    self.root.after(0, lambda: self.status_label.config(
                                        text=f"Saving to {category}...", fg="orange"))
                                    self.root.update()
                                    
                                    saved_count = 0
                                    for i, seg in enumerate(segments):
                                        num = next_num + i
                                        fname = os.path.join(save_dir, f"{category} {num}.wav")
                                        wavfile.write(fname, SAMPLE_RATE, (seg * 32767).astype(np.int16))
                                        saved_count += 1
                                    
                                    self.root.after(0, lambda c=saved_count, cat=category: self.status_label.config(
                                        text=f"Saved {c} sample(s) to {cat} folder", fg="green"))
                        else:
                            self.root.after(0, lambda: self.status_label.config(
                                text="No sound detected above threshold!", fg="orange"))
                    else:
                        # Save without trimming
                        self.root.after(0, lambda: self.status_label.config(
                            text="Choose save location...", fg="orange"))
                        filename = filedialog.asksaveasfilename(
                            defaultextension=".wav",
                            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                            title="Save Recording"
                        )
                        if filename:
                            wavfile.write(filename, SAMPLE_RATE, (recording * 32767).astype(np.int16))
                            self.root.after(0, lambda f=filename: self.status_label.config(
                                text=f"Saved: {f}", fg="green"))
                        else:
                            self.root.after(0, lambda: self.status_label.config(
                                text="Save cancelled", fg="orange"))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="No audio detected!", fg="orange"))
            else:
                self.root.after(0, lambda: self.status_label.config(
                    text="Recording interrupted", fg="orange"))

        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(
                text=f"Error: {str(e)}", fg="red"))

        # Auto-stop if timed mode
        if self.mode_var.get() == "timed":
            self.root.after(0, self.stop_recording)

    def remove_silence(self, recording, threshold, fade_ms=20, gap_ms=150, loop_mode=False):
        """Remove silence from recording and return list of segments"""

        # Convert to mono for analysis
        if len(recording.shape) > 1:
            mono = np.mean(recording, axis=1)
        else:
            mono = recording

        MIN_SOUND_DURATION = 0.05
        MIN_SILENCE_GAP = gap_ms / 1000.0  # Convert ms to seconds
        END_EXTEND_MS = 50  # Extend end by 50ms for smoother tails
        START_EXTEND_MS = 5  # Small extension at start for attack

        is_sound = np.abs(mono) > threshold
        sound_indices = np.where(is_sound)[0]

        print(f"remove_silence: threshold={threshold}, min_gap={MIN_SILENCE_GAP}s")
        print(f"  Total samples: {len(recording)}, sound samples: {len(sound_indices)}")

        if len(sound_indices) == 0:
            print("  No sound detected!")
            return []

        # Loop mode: trim only start and end, keep everything in between
        if loop_mode:
            # Find where actual audio starts and ends
            start_idx = sound_indices[0]
            end_idx = sound_indices[-1]
            
            # Add small buffer at start and end (20ms) for safety
            buffer_samples = int(0.02 * SAMPLE_RATE)
            extended_start = max(0, start_idx - buffer_samples)
            extended_end = min(len(recording), end_idx + buffer_samples)
            
            # Take the entire segment without any processing
            segment = recording[extended_start:extended_end].copy()
            
            # NO fade for loops - needs to be seamless
            print(f"  Loop mode: kept entire segment from {extended_start} to {extended_end}")
            print(f"  Duration: {len(segment)/SAMPLE_RATE:.2f}s")
            return [segment]

        # Normal mode: split into multiple segments
        segments = []
        start_idx = sound_indices[0]
        gaps_found = []

        for i in range(1, len(sound_indices)):
            gap = sound_indices[i] - sound_indices[i-1]
            if gap > MIN_SILENCE_GAP * SAMPLE_RATE:
                gaps_found.append(gap / SAMPLE_RATE)
                end_idx = sound_indices[i-1]
                duration = (end_idx - start_idx) / SAMPLE_RATE
                if duration > MIN_SOUND_DURATION:
                    # Extend start and end
                    extended_start = max(0, start_idx - int(START_EXTEND_MS * SAMPLE_RATE / 1000))
                    extended_end = min(end_idx + int(END_EXTEND_MS * SAMPLE_RATE / 1000), len(recording))
                    segment = recording[extended_start:extended_end].copy()
                    # Apply fade-out
                    segment = self.apply_fade_out(segment, fade_ms)
                    segments.append(segment)
                start_idx = sound_indices[i]

        # Last segment
        last_duration = (sound_indices[-1] - start_idx) / SAMPLE_RATE
        if last_duration > MIN_SOUND_DURATION:
            # Extend start and end
            extended_start = max(0, start_idx - int(START_EXTEND_MS * SAMPLE_RATE / 1000))
            extended_end = min(sound_indices[-1] + 1 + int(END_EXTEND_MS * SAMPLE_RATE / 1000), len(recording))
            segment = recording[extended_start:extended_end].copy()
            # Apply fade-out
            segment = self.apply_fade_out(segment, fade_ms)
            segments.append(segment)

        print(f"  Gaps found: {gaps_found}")
        print(f"  Segments created: {len(segments)}")

        return segments

    def apply_fade_out(self, segment, fade_ms):
        """Apply fade-out to the end of the segment only"""
        fade_samples = int(fade_ms * SAMPLE_RATE / 1000)
        fade_samples = min(fade_samples, len(segment) // 4)
        
        if fade_samples < 10:
            return segment
        
        # Create a smooth exponential fade curve
        t = np.linspace(0, 1, fade_samples)
        fade_curve = np.exp(-3 * t)  # Exponential decay for smoother fade
        
        if len(segment.shape) == 1:
            segment[-fade_samples:] *= fade_curve
        else:
            for ch in range(segment.shape[1]):
                segment[-fade_samples:, ch] *= fade_curve
        
        return segment

def main():
    root = tk.Tk()
    app = RecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
