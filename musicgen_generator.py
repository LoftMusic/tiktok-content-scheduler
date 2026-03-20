"""
MusicGen Generator - Hugging Face
Saved in WAV format manually
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import torch
from transformers import MusicgenForConditionalGeneration, AutoProcessor
import numpy as np
import struct

# Setari
OUTPUT_DIR = r"G:\MIDI PATTERNS\GENERATED"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_wav(filepath, data, sample_rate=32000):
    """Write WAV file manually (no dependencies)."""
    # Convert to 16-bit PCM
    data_int = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    
    # WAV header
    chunk_size = 36 + len(data_int) * 2
    subchunk2_size = len(data_int) * 2
    
    with open(filepath, 'wb') as f:
        # RIFF chunk
        f.write(b'RIFF')
        f.write(struct.pack('<I', chunk_size))
        f.write(b'WAVE')
        
        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # Subchunk1Size (16 for PCM)
        f.write(struct.pack('<H', 1))   # AudioFormat (1 for PCM)
        f.write(struct.pack('<H', 1))   # NumChannels (1 = mono)
        f.write(struct.pack('<I', sample_rate))  # SampleRate
        f.write(struct.pack('<I', sample_rate * 2))  # ByteRate
        f.write(struct.pack('<H', 2))   # BlockAlign
        f.write(struct.pack('<H', 16))  # BitsPerSample
        
        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', subchunk2_size))
        f.write(data_int.tobytes())
    
    print(f"[OK] Saved: {filepath}")

def generate_with_musicgen(prompt, duration=8, output_path=None):
    """Generate audio using MusicGen."""
    
    print(f"[i] Generating: {prompt}")
    print(f"[i] Duration: {duration}s")
    
    # Load model and processor
    print("[1] Loading MusicGen model...")
    model_name = "facebook/musicgen-small"
    model = MusicgenForConditionalGeneration.from_pretrained(model_name)
    processor = AutoProcessor.from_pretrained(model_name)
    
    # Set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"    Using device: {device}")
    
    # Prepare inputs
    print("[2] Preparing inputs...")
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    ).to(device)
    
    # Generate
    print("[3] Generating audio...")
    audio_values = model.generate(
        **inputs,
        do_sample=True,
        guidance_scale=3,
        max_new_tokens=256,
    )
    
    # Convert to numpy and extract mono
    audio_mono = audio_values[0].cpu().numpy()
    
    # Save as WAV
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "musicgen_generated.wav")
    
    write_wav(output_path, audio_mono, 32000)
    
    return output_path

def main():
    print("=" * 60)
    print("MusicGen Generator")
    print("=" * 60)
    
    prompt = "Balkan manele rhythm, A minor key, 100 BPM, saxophone solo, traditional Romanian/Balkan melody"
    
    output_path = generate_with_musicgen(prompt, duration=8)
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Done! Check: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()