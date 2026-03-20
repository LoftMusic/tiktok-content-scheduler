"""
Antrenament Magenta MelodyRNN pe GPU
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

import tensorflow as tf
import magenta
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_train

# Setari
TFRECORDS_PATH = r"G:\MIDI PATTERNS\MAGENTA\melodies.tfrecord"
TRAIN_DIR = r"G:\MIDI PATTERNS\MAGENTA\train"
CHECKPOINT_DIR = os.path.join(TRAIN_DIR, "checkpoints")

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

print("=" * 60)
print("Magenta MelodyRNN Training")
print("=" * 60)

# Configuratie
config_name = "attention_rnn"
print(f"\n[1] Config: {config_name}")

# Get config
config = melody_rnn_model.default_configs[config_name]
print(f"    steps_per_quarter: {config.steps_per_quarter}")
print(f"    min_note: {config.min_note}")
print(f"    max_note: {config.max_note}")

# Train
print(f"\n[2] Training...")
print(f"    Dataset: {TFRECORDS_PATH}")
print(f"    Output: {CHECKPOINT_DIR}")

# Rulăm antrenamentul
melody_rnn_train.run_training(
    config_name=config_name,
    output_dir=CHECKPOINT_DIR,
    sequence_example_file=TFRECORDS_PATH,
    hparams="batch_size=64,rnn_layer_sizes=[128,128]",
    train_seconds=3600,  # 1 ora
)

print(f"\n{'=' * 60}")
print(f"[OK] Training done! Checkpoint: {CHECKPOINT_DIR}")
print(f"{'=' * 60}")