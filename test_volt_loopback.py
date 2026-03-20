import subprocess
import time, os

ffmpeg = r"C:\Users\Studio3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

# Test Volt 1 capture - this should capture whatever audio is playing through Volt 1
print("=== Test: Volt 1 loopback capture (5 seconds) ===")
result = subprocess.run(
    [ffmpeg, '-hide_banner', '-f', 'dshow', '-i', 'audio=INPUT (2- Volt 1)',
     '-t', '5', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
     r'C:\Users\Studio3\.openclaw\workspace\test_volt_loopback.wav'],
    capture_output=True, text=True, timeout=10
)
print("Return code:", result.returncode)
err_lines = result.stderr.strip().split('\n')
for line in err_lines[-8:]:
    if line.strip():
        print("ERR:", line)

wav_path = r'C:\Users\Studio3\.openclaw\workspace\test_volt_loopback.wav'
if os.path.exists(wav_path):
    size = os.path.getsize(wav_path)
    audio_bytes = size - 44
    if audio_bytes > 0:
        duration_sec = audio_bytes / (44100 * 2 * 2)
        print(f"File: {size} bytes, ~{duration_sec:.2f}s duration")
    else:
        print(f"File exists but audio bytes = 0 (probably silence/no loopback)")
        print(f"File size: {size} bytes")
else:
    print("File NOT created")
