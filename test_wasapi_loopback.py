import subprocess, os

ffmpeg = r"C:\Users\Studio3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

# FFmpeg on Windows supports WASAPI directly via -f wasapi
# Let's test with the loopback device
print("=== Test WASAPI loopback via -f wasapi ===")

# Try with the full loopback name
for dev_name in ["MONITOR L/R (2 - Volt 1) (loopback)", "loopback", "default"]:
    print(f"\nTrying: {dev_name}")
    out = rf"C:\Users\Studio3\.openclaw\workspace\test_wasapi_{dev_name.replace(' ','_').replace('/','_').replace('(','_').replace(')','_')[:30]}.wav"
    result = subprocess.run(
        [ffmpeg, '-hide_banner',
         '-f', 'wasapi', '-i', dev_name,
         '-t', '3', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
         '-y', out],
        capture_output=True, text=True, timeout=8
    )
    print(f"Return code: {result.returncode}")
    err_lines = [l for l in result.stderr.split('\n') if l.strip()]
    for l in err_lines[-5:]:
        print(f"  {l}")
    if os.path.exists(out) and os.path.getsize(out) > 44:
        size = os.path.getsize(out)
        dur = (size - 44) / (44100 * 2 * 2)
        print(f"  RESULT: {size} bytes, ~{dur:.2f}s - {'SUCCESS' if dur > 0.5 else 'silence/short'}")

# Also test if sounddevice Python library is available via C4D Python
print("\n=== Test sounddevice via C4D Python ===")
result = subprocess.run(
    [r"C:\Program Files\Maxon Cinema 4D 2024\resource\modules\python\libs\win64\python.exe",
     "-c", "import sounddevice; print(sounddevice.query_loopback_devices())"],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
print(result.stderr[:500] if result.stderr else "")
