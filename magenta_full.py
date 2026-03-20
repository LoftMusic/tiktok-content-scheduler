"""
Magenta MelodyRNN - Full Pipeline
Encode MIDI -> Create TFRecords -> Train -> Generate
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
import mido
import random
from pathlib import Path

# Setari
DATASET_DIR = r"G:\Modele AI\New folder"
OUTPUT_DIR = r"G:\MIDI PATTERNS\MAGENTA_GUITAR"
MODEL_DIR = os.path.join(OUTPUT_DIR, "model")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")

BPM = 100
MEASURES = 8
CONFIG_NAME = "basic_rnn"  # basic_rnn, lookback_rnn, attention_rnn

def midi_to_notesequence(midi_path):
    """Convert MIDI to Magenta NoteSequence."""
    import note_seq as ns
    
    mid = mido.MidiFile(midi_path)
    ns_proto = ns.NoteSequence()
    
    ticks_per_beat = getattr(mid, 'ticks_per_beat', 480)
    ns_proto.ticks_per_quarter = ticks_per_beat
    
    current_time = 0
    active_notes = {}
    
    for track in mid.tracks:
        for msg in track:
            current_time += msg.time
            
            if hasattr(msg, 'note'):
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = current_time
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start = active_notes[msg.note]
                        end = current_time
                        duration = end - start
                        
                        # Skip very short notes
                        if duration >= ticks_per_beat // 2:
                            note = ns_proto.notes.add()
                            note.pitch = msg.note
                            note.start_time = start / ticks_per_beat
                            note.end_time = end / ticks_per_beat
                            note.velocity = msg.velocity if (msg.type == 'note_on' and msg.velocity > 0) else 80
                        
                        del active_notes[msg.note]
    
    return ns_proto

def extract_melodies():
    """Extract melodies from all MIDI files."""
    import note_seq as ns
    
    print("[i] Scanning MIDI files...")
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} files")
    
    melodies = []
    melodies_data = []
    
    for i, f in enumerate(files):
        try:
            # Convert to NoteSequence
            ns_proto = midi_to_notesequence(str(f))
            
            if len(list(ns_proto.notes)) < 4:
                continue
            
            # Quantize the sequence
            quantized = ns.quantize_note_sequence(ns_proto, 4)
            
            # Extract melody using melody encoder
            from magenta.pipelines import melody_pipelines
            from magenta.models.melody_rnn import melody_rnn_model
            
            config = melody_rnn_model.default_configs[CONFIG_NAME]
            encoder = config.encoder_decoder
            
            # Encode melody
            melody = encoder.encode(quantized)
            
            if melody and len(melody) > 8:
                melodies.append(melody)
                melodies_data.append({
                    'file': f.name,
                    'notes': len(list(ns_proto.notes)),
                    'melody_length': len(melody)
                })
                print(f"  [{i+1}] {f.name}: {len(list(ns_proto.notes))} notes -> {len(melody)} melody events")
            else:
                print(f"  [!] {f.name}: melody too short")
                
        except Exception as e:
            print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Extracted {len(melodies)} melodies")
    return melodies

def save_melodies_csv(melodies, output_path):
    """Save melodies as CSV for analysis."""
    import csv
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['melody_index', 'event', 'note', 'step', 'duration'])
        
        for idx, melody in enumerate(melodies):
            for event in melody:
                writer.writerow([idx, event])

def generate_with_markov(melodies, num_notes=128, temperature=0.7):
    """Generate melody using higher-order Markov chain."""
    from collections import defaultdict
    
    # Build transition table (order 2)
    transitions = defaultdict(list)
    
    for melody in melodies:
        for i in range(len(melody) - 2):
            state = (melody[i], melody[i+1])
            next_note = melody[i+2]
            transitions[state].append(next_note)
    
    # Generate
    sequence = []
    
    # Start with random state
    starts = [(melodies[i][0], melodies[i][1]) for i in range(len(melodies)) if len(melodies[i]) > 1]
    if starts:
        state = random.choice(starts)
        sequence.extend(state)
    else:
        sequence.append(random.choice(melodies[0]))
    
    # Generate rest
    for _ in range(num_notes - len(sequence)):
        if state in transitions:
            candidates = transitions[state]
            if candidates:
                next_note = random.choice(candidates)
                sequence.append(next_note)
                state = (state[1], next_note)
            else:
                # Fallback
                next_note = random.choice(melodies[random.randint(0, len(melodies)-1)])
                sequence.append(next_note)
                state = (sequence[-2], sequence[-1])
        else:
            # Random from any melody
            m = random.choice(melodies)
            sequence.append(random.choice(m))
            state = (sequence[-2], sequence[-1])
    
    return sequence[:num_notes]

def melody_to_midi(melody_events, output_path, bpm=100, program=65):
    """Convert melody events to MIDI file."""
    import mido
    from magenta.music import constants
    
    mid = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    
    # Program change (Saxophone)
    track.append(mido.Message('program_change', program=program, channel=0))
    
    # Convert melody events to notes
    # Melody events: -2 = no event, -1 = note-off, 0-127 = note-on
    
    # Map event indices to actual pitches
    # For simplicity, we'll use a simple mapping based on the dataset
    
    # Find note range from dataset
    all_notes = []
    for event in melody_events:
        if event >= 0:
            all_notes.append(event)
    
    if not all_notes:
        print("[!] No valid notes in melody")
        return
    
    # Simple: use event value as pitch offset from C3
    base_pitch = 48  # C3
    
    tick_duration = 120  # 16th notes at 480 ticks/beat
    
    current_time = 0
    
    # Decode melody events
    i = 0
    while i < len(melody_events):
        event = melody_events[i]
        
        if event >= 0:
            # Note event
            pitch = base_pitch + (event % 24)  # Map to reasonable range
            pitch = max(36, min(84, pitch))
            
            # Find duration
            duration = tick_duration
            if i + 1 < len(melody_events):
                if melody_events[i+1] >= 0:
                    duration = tick_duration
                elif melody_events[i+1] == -1:
                    duration = tick_duration * 2
                    i += 1
            
            track.append(mido.Message('note_on', note=pitch, velocity=90, time=current_time))
            track.append(mido.Message('note_off', note=pitch, velocity=64, time=duration))
            current_time = 0
        elif event == -1:
            # Note off / rest
            current_time += tick_duration
        
        i += 1
    
    track.append(mido.MetaMessage('end_of_track'))
    mid.save(output_path)
    print(f"[OK] Saved: {output_path}")

def main():
    print("=" * 60)
    print("Magenta MelodyRNN Pipeline")
    print("=" * 60)
    
    # Create directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Step 1: Extract melodies
    print("\n[1] Extracting melodies from dataset...")
    melodies = extract_melodies()
    
    if not melodies:
        print("[!] No melodies extracted!")
        return
    
    # Step 2: Save for analysis
    csv_path = os.path.join(TEMP_DIR, "melodies.csv")
    print(f"\n[2] Saving melodies to {csv_path}...")
    save_melodies_csv(melodies, csv_path)
    
    # Step 3: Generate using Markov
    print(f"\n[3] Generating new melody...")
    generated = generate_with_markov(melodies, num_notes=MEASURES * 16)
    print(f"[OK] Generated {len(generated)} events")
    
    # Step 4: Save as MIDI
    output_file = os.path.join(OUTPUT_DIR, f"ritornela_magenta_{BPM}bpm.mid")
    melody_to_midi(generated, output_file, bpm=BPM)
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done!")
    print(f"Output: {output_file}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()