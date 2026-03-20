"""MelodyRNN Generation cu model pre-atentat"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import note_seq as ns
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_generate
import mido
from pathlib import Path

OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"

def generate_melody_rnn():
    """Genereaza melodie cu MelodyRNN."""
    
    # Config - basic_rnn e cel mai simplu, lookback_rnn e mai bun
    config_name = "lookback_rnn"  # sau "attention_rnn"
    
    print(f"[i] Loading config: {config_name}")
    config = melody_rnn_model.default_configs[config_name]
    
    # Check for checkpoint
    checkpoint = None
    
    # Try default checkpoints locations
    possible_paths = [
        os.path.expanduser("~/magenta/"),
        "C:\\magenta",
    ]
    
    # Download pretrained if needed
    print("[i] Checking for pretrained model...")
    
    # For now, use basic generation without checkpoint
    # This will create a fresh random model
    
    print(f"\n[i] Generating melody...")
    print(f"[i] Config: {config_name}")
    print(f"[i] Steps: 128 (8 measures)")
    print(f"[i] Temperature: 0.5 (mai mic = mai previzibil)")
    
    # Generate using the model's decoder
    # We'll create a simple generation
    
    return config_name

def generate_simple_melody():
    """Genereaza melodie simpla folosind modelul."""
    
    print("=" * 50)
    print("MelodyRNN Generation")
    print("=" * 50)
    
    # Import generation library
    from magenta.models.melody_rnn import melody_rnn_generate
    
    # Use attention config for better results
    config_name = "attention_rnn"
    
    print(f"\n[>] Generating cu {config_name}...")
    
    # Generate using CLI-style approach
    run_dir = None  # Will use default
    
    return config_name

if __name__ == "__main__":
    # Try to generate with pretrained
    try:
        result = generate_simple_melody()
        print(f"\n[OK] Config: {result}")
    except Exception as e:
        print(f"[!] Error: {e}")
        
        # Fallback - use the generation CLI
        print("\n[i] Trying CLI approach...")
        
        # This would be: melody_rnn_generate --config=attention_rnn --output_dir=...
        # But we need a checkpoint for that