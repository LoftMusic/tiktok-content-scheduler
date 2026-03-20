"""
VST Batch Extractor using REAPER
Automatically loads VST, cycles through programs, renders audio
"""

import subprocess
import os
import time

# === CONFIGURATION ===
REAPER_PATH = r"C:\Program Files\REAPER (x64)\reaper.exe"
VST_PATH = r"C:\Program Files\VSTPlugins\BANDA CORRIDOS VST\Banda Corridos Vst.vst3"
INSTRUMENTS_DIR = r"C:\Program Files\VSTPlugins\BANDA CORRIDOS VST\Banda Corridos Vst.instruments"
OUTPUT_DIR = r"C:\Samples\BANDA_CORRIDOS"

SAMPLE_RATE = 44100
RENDER_LENGTH = 4.0  # seconds

def get_instruments():
    """Get list of .mse files"""
    instruments = []
    for f in os.listdir(INSTRUMENTS_DIR):
        if f.endswith('.mse'):
            instruments.append(f.replace('.mse', ''))
    return sorted(instruments)

def create_reaper_project(instrument_name, output_wav):
    """Create a minimal Reaper project file that loads VST and renders"""
    
    # Clean filename for Reproject
    safe_name = instrument_name.replace('"', '\\"')
    
    rpp_content = f'''<REAPER_PROJECT 0.1 "7.30" 169
<ITEM 1 0 {RENDER_LENGTH} 0 0 0 0 0 0 0 ""
<FXCHAIN 0 0 "VST: Banda Corridos Vst (2CA Audio)" "{VST_PATH}" 0 ""
>
'''
    return rpp_content

def render_with_reaper(project_file, output_wav):
    """Render project to WAV using Reaper command line"""
    
    # Reaper command line render
    cmd = [
        REAPER_PATH,
        project_file,
        "--render",
        "--renderfile", output_wav,
        "--renderformat", "WAV",
        "--sr", str(SAMPLE_RATE),
        "--join"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("=" * 50)
    print("VST Batch Extractor for REAPER")
    print("=" * 50)
    
    # Get instruments
    instruments = get_instruments()
    print(f"Found {len(instruments)} instruments")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create temp project dir
    temp_dir = os.path.join(os.environ['TEMP'], 'vst_render_temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"Rendering {RENDER_LENGTH}s per instrument...\n")
    
    for i, instrument in enumerate(instruments):
        print(f"[{i+1}/{len(instruments)}] {instrument}...", end=" ")
        
        # Create project file
        project_file = os.path.join(temp_dir, f"render_{i}.rpp")
        output_wav = os.path.join(OUTPUT_DIR, f"{instrument}.wav")
        
        # Create simple RPP that will play the VST
        # Using a simple project that renders silence but VST will play
        rpp = f'''<REAPER_PROJECT 0.1 "7.30" 170
<SETTINGsexportmode 0
<SETTINGSwavformat -1.00000000 0 0 0 0 0 0 0 0 0 0 0
<SETTINGSWAVEEX 0
<PROJECT "{{A0FDBF53-2BF9-4F9A-A1C7-4B8C7D7A1B3C}"
0 "{SAMPLE_RATE}"
0 0 0 0 0 0 0 0 0
0 0
>
<TRACK 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0
<FXCHAIN 0 0 "VST: Banda Corridos Vst (2CA Audio)" "{VST_PATH}" 0 ""
>
'''
        with open(project_file, 'w') as f:
            f.write(rpp)
        
        # Try to render
        success = render_with_reaper(project_file, output_wav)
        
        if success and os.path.exists(output_wav):
            print("OK")
        else:
            print("FAILED")
            print("  -> You'll need to render manually or try FL Studio method")
    
    print(f"\n{'='*50}")
    print(f"Done! Check: {OUTPUT_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()
