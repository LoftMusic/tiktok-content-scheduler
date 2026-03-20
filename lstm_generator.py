"""
PyTorch LSTM MIDI Generator
Antrenează un model LSTM să învețe ritornele și să genereze noi melodii
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import mido
import numpy as np
from pathlib import Path
from collections import Counter
import random

# Setari
DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"
MODEL_PATH = os.path.join(OUTPUT_DIR, "lstm_model.pt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Constants
STEPS_PER_QUARTER = 4
MAX_NOTE = 84
MIN_NOTE = 36

def extract_events_from_midi(midi_path):
    """Extract note events from MIDI file."""
    mid = mido.MidiFile(midi_path)
    events = []
    
    ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
    
    for track in mid.tracks:
        current_time = 0
        notes_on = {}
        
        for msg in track:
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_on[msg.note] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in notes_on:
                    start = notes_on[msg.note]
                    end = current_time
                    duration = end - start
                    
                    # Convert to steps (16th notes)
                    step_duration = max(1, int(duration / (ticks_per_beat / 4)))
                    
                    events.append({
                        'pitch': msg.note,
                        'duration': step_duration
                    })
                    
                    del notes_on[msg.note]
    
    return events

def events_to_tensor(events):
    """Convert events to tensor representation."""
    # Format: [pitch, duration] for each event
    tensor = []
    for e in events:
        pitch_norm = (e['pitch'] - MIN_NOTE) / (MAX_NOTE - MIN_NOTE)
        dur_norm = min(e['duration'] / 16, 1.0)  # Normalize duration to [0, 1]
        tensor.append([pitch_norm, dur_norm])
    
    return torch.tensor(tensor, dtype=torch.float32)

def tensor_to_events(tensor):
    """Convert tensor back to events."""
    events = []
    for t in tensor:
        pitch = int(t[0] * (MAX_NOTE - MIN_NOTE) + MIN_NOTE)
        pitch = max(MIN_NOTE, min(MAX_NOTE, pitch))
        
        duration = int(t[1] * 16)
        duration = max(1, duration)
        
        events.append({'pitch': pitch, 'duration': duration})
    
    return events

def save_midi_from_events(events, output_path, bpm=100):
    """Save events as MIDI file."""
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(mido.Message('program_change', program=65, channel=0))  # Sax
    
    for e in events:
        pitch = e['pitch']
        duration_ticks = e['duration'] * 30
        
        track.append(mido.Message('note_on', note=pitch, velocity=90, time=0))
        track.append(mido.Message('note_off', note=pitch, velocity=64, time=duration_ticks))
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

class MidiDataset(Dataset):
    def __init__(self, dataset_dir, max_len=128):
        self.files = list(Path(dataset_dir).glob("*.mid"))
        self.data = []
        
        for f in self.files:
            try:
                events = extract_events_from_midi(str(f))
                if events:
                    tensor = events_to_tensor(events)
                    # Truncate or pad
                    if len(tensor) > max_len:
                        tensor = tensor[:max_len]
                    elif len(tensor) < max_len:
                        pad = torch.zeros(max_len - len(tensor), 2)
                        tensor = torch.cat([tensor, pad], dim=0)
                    self.data.append(tensor)
            except Exception as e:
                print(f"Error {f}: {e}")
        
        print(f"Loaded {len(self.data)} melodies")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        seq = self.data[idx]
        return seq[:-1], seq[1:]  # Input: all but last, Target: all but first

class LSTMGenerator(nn.Module):
    def __init__(self, input_size=2, hidden_size=128, num_layers=2, output_size=2):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
    
    def forward(self, x, hidden=None):
        if hidden is None:
            hidden = self.init_hidden(x.size(0))
        
        out, hidden = self.lstm(x, hidden)
        out = self.fc(self.relu(out))
        return out, hidden
    
    def init_hidden(self, batch_size):
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)

def train_model():
    """Train the LSTM model."""
    print("=" * 60)
    print("Training LSTM MIDI Generator")
    print("=" * 60)
    
    # Load dataset
    print("\n[1] Loading dataset...")
    dataset = MidiDataset(DATASET_DIR)
    if len(dataset.data) == 0:
        print("[!] No data loaded!")
        return
    
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    
    # Model
    print("\n[2] Building model...")
    model = LSTMGenerator().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print(f"    Model: LSTM(input=2, hidden=128, layers=2, output=2)")
    
    # Training
    print("\n[3] Training...")
    num_epochs = 50
    
    for epoch in range(num_epochs):
        total_loss = 0
        for batch_idx, (inputs, targets) in enumerate(dataloader):
            inputs = inputs.to(device)
            targets = targets.to(device)
            
            optimizer.zero_grad()
            
            outputs, _ = model(inputs)
            loss = criterion(outputs, targets)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        print(f"  Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")
    
    # Save model
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"\n[OK] Model saved: {MODEL_PATH}")
    
    return model

def generate_melody(model, length=128, temperature=0.7):
    """Generate melody using the trained model."""
    model.eval()
    
    # Start with random note
    start_pitch = random.randint(MIN_NOTE, MAX_NOTE)
    start_pitch_norm = (start_pitch - MIN_NOTE) / (MAX_NOTE - MIN_NOTE)
    start_dur = 0.5
    
    generated = [[start_pitch_norm, start_dur]]
    
    with torch.no_grad():
        seq = torch.tensor([generated], dtype=torch.float32).to(device)
        hidden = model.init_hidden(1)
        
        for _ in range(length - 1):
            output, hidden = model(seq, hidden)
            
            # Sample from output
            output = output[0, -1]
            
            # Add temperature
            pitch_pred = output[0].item()
            dur_pred = output[1].item()
            
            # Denormalize
            pitch = int(pitch_pred * (MAX_NOTE - MIN_NOTE) + MIN_NOTE)
            pitch = max(MIN_NOTE, min(MAX_NOTE, pitch))
            
            duration = int(dur_pred * 16)
            duration = max(1, duration)
            
            generated.append([
                (pitch - MIN_NOTE) / (MAX_NOTE - MIN_NOTE),
                min(duration / 16, 1.0)
            ])
            
            # Update sequence
            seq = torch.tensor([generated], dtype=torch.float32).to(device)
    
    return tensor_to_events(torch.tensor(generated))

def main():
    print("=" * 60)
    print("PyTorch LSTM MIDI Generator")
    print("=" * 60)
    
    # Train
    model = train_model()
    
    if model is None:
        print("[!] Training failed!")
        return
    
    # Generate
    print("\n[4] Generating melodies...")
    
    for var in range(1, 4):
        melody = generate_melody(model, length=128, temperature=0.7)
        
        output_path = os.path.join(OUTPUT_DIR, f"lstm_generated_var{var}.mid")
        save_midi_from_events(melody, output_path, bpm=100)
        
        print(f"  [{var}] Saved: {output_path}")
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()