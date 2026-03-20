"""
TFRecords Generator - Corect pentru Magenta
Folosește note_seq pentru generarea corectă
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import note_seq as ns
from note_seq import constants
from pathlib import Path
import tensorflow as tf

DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\MAGENTA"
TFRECORDS_PATH = os.path.join(OUTPUT_DIR, "melodies.tfrecord")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_melody_events(midi_path):
    """Extract melody events from MIDI using note_seq."""
    ns_proto = ns.midi_file_to_note_sequence(midi_path)
    
    # Quantize
    quantized = ns.quantize_note_sequence(ns_proto, steps_per_quarter=4)
    
    # Convert to melody events
    # Use MelodyExtractor from Magenta
    from magenta.pipelines.melody_pipelines import MelodyExtractor
    extractor = MelodyExtractor(min_bars=1, max_steps=512, min_unique_pitches=2, ignore_polyphonic_notes=True)
    
    result = extractor.transform(quantized)
    
    if result and len(result) > 0:
        melody = result[0]
        return list(melody._events)
    return None

def create_tfrecord_from_events(events, writer):
    """Create a single TFRecord example from melody events."""
    # Magenta expects:
    # - features/inputs: float32 array of note events
    # - features/length: int64 scalar
    
    # Convert events to float32
    inputs = [float(e) for e in events]
    
    example = tf.train.Example()
    
    # Length feature
    example.features.feature['length'].int64_list.value.append(len(events))
    
    # Inputs feature (note events as float32)
    example.features.feature['inputs'].float_list.value.extend(inputs)
    
    writer.write(example.SerializeToString())

def main():
    print("=" * 60)
    print("TFRecords Generator (Magenta-compatible)")
    print("=" * 60)
    
    # Extract all melodies
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} MIDI files")
    
    count = 0
    
    with tf.io.TFRecordWriter(TFRECORDS_PATH) as writer:
        for i, f in enumerate(files):
            try:
                events = extract_melody_events(str(f))
                if events:
                    create_tfrecord_from_events(events, writer)
                    count += 1
                    print(f"  [{i+1}] {f.name}: {len(events)} events -> saved")
            except Exception as e:
                print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Saved {count} melodies to {TFRECORDS_PATH}")
    
    print(f"\n{'=' * 60}")
    print("TFRecords ready!")
    print(f"Path: {TFRECORDS_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()