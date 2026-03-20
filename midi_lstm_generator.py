# -*- coding: utf-8 -*-
"""
MIDI Generator cu LSTM real (PyTorch)
Antrenează un model LSTM care generează pattern-uri MIDI fidele datasetului.
"""

import os
import sys
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from collections import defaultdict

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Setări
DATASET_DIR = r"G:\Modele AI\New folder"
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED_LSTM_TORCH"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEQUENCE_LENGTH = 16
HIDDEN_SIZE = 256
NUM_LAYERS = 2
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.001

print(f"Using device: {DEVICE}")

def extract_midi_events(midi_path):
    """Extract note events from MIDI file."""
    import mido
    
    try:
        mid = mido.MidiFile(midi_path)
        events = []
        
        ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
        
        for track in mid.tracks:
            current_time = 0
            active_notes = {}
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = current_time
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start = active_notes[msg.note]
                        end = current_time
                        duration = end - start
                        
                        duration_16th = max(1, int(duration / (ticks_per_beat / 4)))
                        
                        events.append({
                            'pitch': msg.note,
                            'duration': duration_16th,
                            'velocity': msg.velocity
                        })
                        
                        del active_notes[msg.note]
        
        return events
    except Exception as e:
        return []

def build_vocabulary(all_events):
    """Build pitch vocabulary."""
    pitches = set()
    
    for events in all_events:
        for e in events:
            pitches.add(e['pitch'])
    
    pitch_list = sorted(list(pitches))
    pitch_to_idx = {p: i+1 for i, p in enumerate(pitch_list)}  # +1 pentru padding
    idx_to_pitch = {i+1: p for i, p in enumerate(pitch_list)}
    pitch_to_idx[0] = 0  # padding
    idx_to_pitch[0] = 0
    
    return pitch_list, pitch_to_idx, idx_to_pitch, len(pitch_list) + 1

class MIDIDataset(Dataset):
    def __init__(self, all_events, pitch_to_idx, seq_length=16):
        self.sequences = []
        self.labels = []
        
        for events in all_events:
            if len(events) < seq_length + 1:
                continue
            
            for i in range(len(events) - seq_length):
                seq = [pitch_to_idx.get(e['pitch'], 0) for e in events[i:i + seq_length]]
                next_pitch = pitch_to_idx.get(events[i + seq_length]['pitch'], 0)
                
                self.sequences.append(seq)
                self.labels.append(next_pitch)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return torch.tensor(self.sequences[idx], dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)

class LSTMModel(nn.Module):
    def __init__(self, vocab_size, hidden_size, num_layers):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, x, hidden=None):
        embed = self.embedding(x)
        output, hidden = self.lstm(embed, hidden)
        output = self.fc(output[:, -1, :])  # Doar ultimul timestep
        return output, hidden
    
    def init_hidden(self, batch_size):
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(DEVICE)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(DEVICE)
        return (h0, c0)

def train_model(model, dataloader, epochs, lr):
    """Train the LSTM model."""
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (seq, label) in enumerate(dataloader):
            seq = seq.to(DEVICE)
            label = label.to(DEVICE)
            
            optimizer.zero_grad()
            output, _ = model(seq)
            loss = criterion(output, label)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    return model

def generate_melody(model, seed_sequence, pitch_to_idx, idx_to_pitch, seq_length=16, num_generate=64, temperature=0.8):
    """Generate melody using trained LSTM model."""
    model.eval()
    
    generated = list(seed_sequence)
    
    with torch.no_grad():
        for _ in range(num_generate):
            # Prepare input
            if len(generated) < seq_length:
                seq = generated + [0] * (seq_length - len(generated))
            else:
                seq = generated[-seq_length:]
            
            seq_tensor = torch.tensor([seq], dtype=torch.long).to(DEVICE)
            
            # Get prediction
            output, _ = model(seq_tensor)
            
            # Apply temperature
            probs = torch.softmax(output / temperature, dim=1)
            
            # Sample
            next_idx = torch.multinomial(probs, 1).item()
            
            # Convert to pitch
            next_pitch = idx_to_pitch.get(next_idx, generated[-1] if generated else 60)
            
            generated.append(next_pitch)
    
    return generated

def midi_events_to_file(events, output_path, bpm=100, program=25):
    """Convert events to MIDI file."""
    import mido
    
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    
    track.append(mido.Message('program_change', program=program, channel=0))
    
    current_tick = 0
    for event in events:
        if isinstance(event, int):
            pitch = event
            duration = 4
        else:
            pitch = event['pitch']
            duration = event.get('duration', 4)
        
        pitch = max(36, min(84, pitch))
        duration_ticks = duration * 30
        
        track.append(mido.Message('note_on', note=pitch, velocity=90, time=current_tick))
        track.append(mido.Message('note_off', note=pitch, velocity=64, time=duration_ticks))
        current_tick = 0
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)

def main():
    print("=" * 60)
    print("MIDI Generator cu LSTM (PyTorch)")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Extract events
    print("\n[1] Extracting MIDI events...")
    import glob
    files = glob.glob(os.path.join(DATASET_DIR, "*.mid"))
    print(f"Found {len(files)} files")
    
    all_events = []
    for f in files:
        events = extract_midi_events(f)
        if events:
            all_events.append(events)
    
    print(f"Loaded {len(all_events)} melodies")
    
    if not all_events:
        print("[!] No events extracted!")
        return
    
    # Build vocabulary
    print("\n[2] Building vocabulary...")
    pitch_list, pitch_to_idx, idx_to_pitch, vocab_size = build_vocabulary(all_events)
    print(f"Vocabulary size: {vocab_size}")
    
    # Create dataset
    print("\n[3] Creating dataset...")
    dataset = MIDIDataset(all_events, pitch_to_idx, SEQUENCE_LENGTH)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    print(f"Dataset size: {len(dataset)} sequences")
    
    # Create model
    print("\n[4] Creating LSTM model...")
    model = LSTMModel(vocab_size, HIDDEN_SIZE, NUM_LAYERS).to(DEVICE)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters())}")
    
    # Train
    print(f"\n[5] Training for {EPOCHS} epochs...")
    model = train_model(model, dataloader, EPOCHS, LEARNING_RATE)
    
    # Generate
    print(f"\n[6] Generating melody...")
    seed = [pitch_to_idx.get(e['pitch'], 0) for e in all_events[0][:SEQUENCE_LENGTH]]
    generated_pitches = generate_melody(model, seed, pitch_to_idx, idx_to_pitch, SEQUENCE_LENGTH, num_generate=64, temperature=0.8)
    
    # Convert to events
    generated_events = [{'pitch': p, 'duration': random.choice([4, 8, 16])} for p in generated_pitches]
    
    # Save
    output_file = os.path.join(OUTPUT_DIR, f"ritornela_lstm_torch_{EPOCHS}epochs.mid")
    midi_events_to_file(generated_events, output_file, bpm=100, program=25)
    
    print(f"[OK] Saved: {output_file}")
    print(f"[OK] Generated {len(generated_events)} notes")
    
    # Save model
    model_path = os.path.join(OUTPUT_DIR, "lstm_model.pt")
    torch.save(model.state_dict(), model_path)
    print(f"[OK] Saved model: {model_path}")
    
    print(f"\n{'=' * 60}")
    print("[OK] Done!")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
