import subprocess
import time

ffmpeg = r"C:\Users\Studio3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

# Test actual 3-second capture to a file
print("=== Test: SoundGrid capture 3 seconds ===")
result = subprocess.run(
    [ffmpeg, '-f', 'dshow', '-i', 'audio=Line In /Microphone (Waves SoundGrid)',
     '-t', '3', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
     r'C:\Users\Studio3\.openclaw\workspace\test_capture.wav'],
    capture_output=True, text=True, timeout=10
)
print("Return code:", result.returncode)
# Show last 10 lines of stderr (FFmpeg outputs to stderr)
err_lines = result.stderr.strip().split('\n')
for line in err_lines[-10:]:
    print("ERR:", line)

# Check if file exists and has content
import os
wav_path = r'C:\Users\Studio3\.openclaw\workspace\test_capture.wav'
if os.path.exists(wav_path):
    size = os.path.getsize(wav_path)
    print(f"File size: {size} bytes")
    # WAV header is 44 bytes, so audio bytes = size - 44
    audio_bytes = size - 44
    if audio_bytes > 0:
        duration_sec = audio_bytes / (44100 * 2 * 2)
        print(f"Approximate duration: {duration_sec:.2f}s")
else:
    print("File was NOT created")
