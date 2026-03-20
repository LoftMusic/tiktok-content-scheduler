import subprocess, os

ffmpeg = r"C:\Users\Studio3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

# Try WASAPI loopback with the specific device name Audacity uses
# FFmpeg on Windows can sometimes capture WASAPI loopback via DirectShow with the right device name
devices_to_try = [
    "MONITOR L/R (2 - Volt 1) (loopback)",
    "MONITOR L/R (2 - Volt 1)",
    "Volt 1 (loopback)",
    "2 - Volt 1:loopback",
    "MONITOR",
]

for dev in devices_to_try:
    print(f"\n=== Testing: {dev} ===")
    out_file = rf"C:\Users\Studio3\.openclaw\workspace\test_{dev.replace(' ','_').replace('(','_').replace(')','_')}.wav"
    result = subprocess.run(
        [ffmpeg, '-hide_banner',
         '-f', 'dshow', '-i', f'audio={dev}',
         '-t', '3', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
         '-y', out_file],
        capture_output=True, text=True, timeout=8
    )
    print(f"Return code: {result.returncode}")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 44:
        size = os.path.getsize(out_file)
        dur = (size - 44) / (44100 * 2 * 2)
        print(f"SUCCESS: {size} bytes, ~{dur:.2f}s")
    else:
        # Show error from stderr
        err_lines = [l for l in result.stderr.split('\n') if 'error' in l.lower() or 'invalid' in l.lower() or 'could not' in l.lower()]
        for l in err_lines[:3]:
            print(f"ERR: {l}")

# Also try with -f waveout (native Windows audio)
print("\n=== Try -f waveout: default ===")
result = subprocess.run(
    [ffmpeg, '-hide_banner', '-f', 'waveout', '-i', 'default',
     '-t', '3', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
     '-y', r'C:\Users\Studio3\.openclaw\workspace\test_waveout.wav'],
    capture_output=True, text=True, timeout=8
)
print(f"Return code: {result.returncode}")
if os.path.exists(r'C:\Users\Studio3\.openclaw\workspace\test_waveout.wav'):
    size = os.path.getsize(r'C:\Users\Studio3\.openclaw\workspace\test_waveout.wav')
    if size > 44:
        dur = (size - 44) / (44100 * 2 * 2)
        print(f"SUCCESS: {size} bytes, ~{dur:.2f}s")
