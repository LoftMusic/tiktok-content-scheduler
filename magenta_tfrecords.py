"""
Magenta TFRecords Generator
Convertește melodii în format TFRecords pentru antrenament
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import note_seq as ns
from magenta.pipelines.melody_pipelines import MelodyExtractor
from pathlib import Path
import tensorflow as tf

DATASET_DIR = r"C:\midi_dataset"
OUTPUT_DIR = r"G:\MIDI PATTERNS\MAGENTA"
TFRECORDS_PATH = os.path.join(OUTPUT_DIR, "melodies.tfrecord")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_melody_events(midi_path):
    """Extract melody events from MIDI."""
    ns_proto = ns.midi_file_to_note_sequence(midi_path)
    quantized = ns.quantize_note_sequence(ns_proto, 4)
    
    extractor = MelodyExtractor(min_bars=1, max_steps=512, min_unique_pitches=2, ignore_polyphonic_notes=True)
    result = extractor.transform(quantized)
    
    if result and len(result) > 0:
        return list(result[0]._events)
    return None

def main():
    print("=" * 60)
    print("TFRecords Generator")
    print("=" * 60)
    
    # Extract all melodies
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} MIDI files")
    
    all_events = []
    
    for i, f in enumerate(files):
        events = extract_melody_events(str(f))
        if events:
            all_events.append(events)
            print(f"  [{i+1}] {f.name}: {len(events)} events")
    
    print(f"\n[OK] Extracted {len(all_events)} melodies")
    print(f"[OK] Total events: {sum(len(e) for e in all_events)}")
    
    # Write TFRecords
    print(f"\n[2] Writing TFRecords to {TFRECORDS_PATH}...")
    
    with tf.io.TFRecordWriter(TFRECORDS_PATH) as writer:
        for events in all_events:
            # Convert events to a simple format
            # Format: [len_events, event1, event2, ...]
            example = tf.train.Example()
            example.features.feature['length'].int64_list.value.append(len(events))
            
            # Add events as bytes
            events_bytes = ''.join(str(e) + ',' for e in events).encode()
            example.features.feature['events'].bytes_list.value.append(events_bytes)
            
            writer.write(example.SerializeToString())
    
    print(f"[OK] Saved TFRecords: {TFRECORDS_PATH}")
    
    print(f"\n{'=' * 60}")
    print("TFRecords created!")
    print(f"Path: {TFRECORDS_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()