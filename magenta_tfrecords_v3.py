"""
TFRecords Generator - Correct SequenceExample format for Magenta
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import note_seq as ns
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
    
    # Use Magenta MelodyExtractor
    from magenta.pipelines.melody_pipelines import MelodyExtractor
    extractor = MelodyExtractor(min_bars=1, max_steps=512, min_unique_pitches=2, ignore_polyphonic_notes=True)
    
    result = extractor.transform(quantized)
    
    if result and len(result) > 0:
        melody = result[0]
        return list(melody._events)
    return None

def create_tfrecord_sequence_example(events, writer):
    """
    Create SequenceExample for Magenta.
    Format:
    - context: length (int64)
    - feature_lists: inputs (float32 array)
    """
    example = tf.train.SequenceExample()
    
    # Context feature: length
    example.context.feature['length'].int64_list.value.append(len(events))
    
    # Feature list: inputs (note events)
    # Each frame is a single float (the event value)
    for event in events:
        feature = example.feature_lists.feature_list['inputs'].feature.add()
        feature.float_list.value.append(float(event))
    
    writer.write(example.SerializeToString())

def main():
    print("=" * 60)
    print("TFRecords Generator (Magenta SequenceExample)")
    print("=" * 60)
    
    files = list(Path(DATASET_DIR).glob("*.mid"))
    print(f"[i] Found {len(files)} MIDI files")
    
    count = 0
    
    with tf.io.TFRecordWriter(TFRECORDS_PATH) as writer:
        for i, f in enumerate(files):
            try:
                events = extract_melody_events(str(f))
                if events:
                    create_tfrecord_sequence_example(events, writer)
                    count += 1
                    print(f"  [{i+1}] {f.name}: {len(events)} events -> saved")
            except Exception as e:
                print(f"  [!] {f.name}: {e}")
    
    print(f"\n[OK] Saved {count} sequences to {TFRECORDS_PATH}")
    
    print(f"\n{'=' * 60}")
    print("TFRecords ready!")
    print(f"Path: {TFRECORDS_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()