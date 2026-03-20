import subprocess

ffmpeg = r"C:\Users\Studio3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

# Test 1: Try NVIDIA virtual audio device
print("=== Test 1: NVIDIA Virtual Audio Device ===")
result = subprocess.run(
    [ffmpeg, '-f', 'dshow', '-i', 'audio=NVIDIA Virtual Audio Device (Wave Extensible) (WDM)', '-t', '1', '-f', 'wav', 'nul'],
    capture_output=True, text=True, timeout=5
)
print("STDOUT:", result.stdout[:200] if result.stdout else "(empty)")
print("STDERR:", result.stderr[:500] if result.stderr else "(empty)")
print("Return code:", result.returncode)

# Test 2: Try SoundGrid as capture device
print("\n=== Test 2: SoundGrid capture ===")
result2 = subprocess.run(
    [ffmpeg, '-f', 'dshow', '-i', 'audio=Line In /Microphone (Waves SoundGrid)', '-t', '1', '-f', 'wav', 'nul'],
    capture_output=True, text=True, timeout=5
)
print("STDOUT:", result2.stdout[:200] if result2.stdout else "(empty)")
print("STDERR:", result2.stderr[:500] if result2.stderr else "(empty)")
print("Return code:", result2.returncode)

# Test 3: Try default audio device
print("\n=== Test 3: Default audio device (empty string) ===")
result3 = subprocess.run(
    [ffmpeg, '-f', 'dshow', '-i', 'audio=', '-t', '1', '-f', 'wav', 'nul'],
    capture_output=True, text=True, timeout=5
)
print("STDOUT:", result3.stdout[:200] if result3.stdout else "(empty)")
print("STDERR:", result3.stderr[:500] if result3.stderr else "(empty)")
print("Return code:", result3.returncode)
