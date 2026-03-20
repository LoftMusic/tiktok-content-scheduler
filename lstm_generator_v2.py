"""
PyTorch LSTM MIDI Generator - Improved
Cu sampling inteligent și pattern preservation
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import mido
import numpy as np
from pathlib import Path
import random

# Setari
DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"
MODEL_PATH = os.path.join(OUTPUT_DIR, "lstm_model.pt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

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
                    
                    step_duration = max(1, int(duration / (ticks_per_beat / 4)))
                    
                    events.append({
                        'pitch': msg.note,
                        'duration': step_duration
                    })
                    
                    del notes_on[msg.note]
    
    return events

def events_to_tensor(events):
    """Convert events to tensor representation."""
    tensor = []
    for e in events:
        pitch_norm = (e['pitch'] - MIN_NOTE) / (MAX_NOTE - MIN_NOTE)
        dur_norm = min(e['duration'] / 16, 1.0)
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
    track.append(mido.Message('program_change', program=65, channel=0))
    
    for e in events:
        pitch = e['pitch']
        duration_ticks = e['duration'] * 30
        
        track.append(mido.Message('note_on', note=pitch, velocity=90, time=0))
        track.append(mido.Message('note_off', note=pitch, velocity=64, time=duration_ticks))
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

class MidiDataset(Dataset):
    def __init__(self, dataset_dir, max_len=64):
        self.files = list(Path(dataset_dir).glob("*.mid"))
        self.data = []
        
        for f in self.files:
            try:
                events = extract_events_from_midi(str(f))
                if events:
                    tensor = events_to_tensor(events)
                    # Truncate to max_len
                    if len(tensor) > max_len:
                        tensor = tensor[:max_len]
                    # Pad to max_len
                    if len(tensor) < max_len:
                        pad = torch.zeros(max_len - len(tensor), 2)
                        tensor = torch.cat([tensor, pad], dim=0)
                    self.data.append(tensor)
            except Exception as e:
                print(f"Error {f}: {e}")
        
        print(f"Loaded {len(self.data)} melodies (max_len={max_len})")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        seq = self.data[idx]
        return seq[:-1], seq[1:]

class LSTMGenerator(nn.Module):
    def __init__(self, input_size=2, hidden_size=256, num_layers=3, output_size=2):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x, hidden=None):
        if hidden is None:
            hidden = self.init_hidden(x.size(0))
        
        out, hidden = self.lstm(x, hidden)
        out = self.dropout(self.fc(out))
        return out, hidden
    
    def init_hidden(self, batch_size):
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)

def top_k_sampling(logits, k=5, temperature=0.8):
    """Sample from top-k predictions with temperature."""
    # Apply temperature
    logits = logits / temperature
    
    # Get top-k
    top_k = torch.topk(logits, min(k, len(logits)))
    top_values = top_k.values
    top_indices = top_k.indices
    
    # Softmax
    probs = torch.softmax(top_values, dim=0)
    
    # Sample
    sample_idx = torch.multinomial(probs, 1).item()
    return top_indices[sample_idx].item()

def train_model():
    """Train the LSTM model."""
    print("=" * 60)
    print("Training LSTM MIDI Generator (Improved)")
    print("=" * 60)
    
    print("\n[1] Loading dataset...")
    dataset = MidiDataset(DATASET_DIR, max_len=64)
    if len(dataset.data) == 0:
        print("[!] No data loaded!")
        return None
    
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    print("\n[2] Building model...")
    model = LSTMGenerator(input_size=2, hidden_size=256, num_layers=3, output_size=2).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print("\n[3] Training...")
    num_epochs = 300
    
    for epoch in range(num_epochs):
        total_loss = 0
        for inputs, targets in dataloader:
            inputs = inputs.to(device)
            targets = targets.to(device)
            
            optimizer.zero_grad()
            outputs, _ = model(inputs)
            loss = criterion(outputs, targets)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 50 == 0:
            print(f"  Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")
    
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"\n[OK] Model saved: {MODEL_PATH}")
    
    return model

def generate_melody(model, dataset, length=128, temperature=0.8, top_k=5, bpm=100, key_root=57, scale='minor'):
    """Generate melody with improved sampling."""
    model.eval()
    
    # Scale for key constraints
    scales = {
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'major': [0, 2, 4, 5, 7, 9, 11],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
    }
    scale_notes = [key_root + s for s in scales.get(scale, scales['minor'])]
    
    def pitch_in_scale(pitch):
        return (pitch % 12) in [s % 12 for s in scale_notes]
    
    def closest_scale_pitch(pitch):
        return min(scale_notes, key=lambda x: min(
            abs(pitch - x), abs(pitch - x - 12), abs(pitch - x + 12)
        ))
    
    # Start with a note from dataset
    start_melody = random.choice(dataset.data)
    start_note = start_melody[0].cpu().numpy()
    
    generated = [list(start_note)]
    
    with torch.no_grad():
        seq = torch.tensor([generated], dtype=torch.float32).to(device)
        hidden = model.init_hidden(1)
        
        for i in range(length - 1):
            output, hidden = model(seq, hidden)
            
            output = output[0, -1]
            
            pitch_pred = output[0].item()
            dur_pred = output[1].item()
            
            # Add noise
            pitch_pred += torch.randn(1).item() * 0.1 * temperature
            dur_pred += torch.randn(1).item() * 0.05 * temperature
            
            # Denormalize
            pitch = int(pitch_pred * (MAX_NOTE - MIN_NOTE) + MIN_NOTE)
            pitch = max(MIN_NOTE, min(MAX_NOTE, pitch))
            
            # Force to scale
            if not pitch_in_scale(pitch):
                pitch = closest_scale_pitch(pitch)
            
            duration = int(dur_pred * 16)
            duration = max(1, min(duration, 32))
            
            generated.append([
                (pitch - MIN_NOTE) / (MAX_NOTE - MIN_NOTE),
                min(duration / 16, 1.0)
            ])
            
            seq = torch.tensor([generated], dtype=torch.float32).to(device)
    
    return tensor_to_events(torch.tensor(generated)), bpm

def main():
    print("=" * 60)
    print("PyTorch LSTM MIDI Generator (Improved)")
    print("=" * 60)
    
    model = train_model()
    
    if model is None:
        print("[!] Training failed!")
        return
    
    dataset = MidiDataset(DATASET_DIR, max_len=64)
    
    # Generate variations with different parameters
    print("\n[4] Generating melodies...")
    
    variations = [
        ('Amin', 126),
        ('Amin', 100),
        ('Emin', 126),
    ]
    
    for key_name, bpm in variations:
        key_map = {'Amin': 57, 'Emin': 52, 'Dmin': 50}
        key_root = key_map.get(key_name, 57)
        
        melody, _ = generate_melody(
            model, dataset, length=128, 
            temperature=0.8, top_k=5,
            bpm=bpm, key_root=key_root, scale='minor'
        )
        
        output_path = os.path.join(OUTPUT_DIR, f"lstm_{key_name}_{bpm}bpm.mid")
        save_midi_from_events(melody, output_path, bpm=bpm)
        
        print(f"  [{key_name}][{bpm}bpm] Saved: {output_path}")
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()