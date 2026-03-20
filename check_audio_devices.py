import sys
print("Python:", sys.version)

# Try to list audio devices
try:
    import subprocess
    ffmpeg_path = r"C:\Users\Studio3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
    
    # List dshow devices
    result = subprocess.run(
        [ffmpeg_path, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
        capture_output=True, text=True, timeout=10
    )
    print("\n=== DirectShow Devices ===")
    for line in result.stderr.split('\n'):
        if 'audio' in line.lower() or '(audio' in line.lower():
            print(line)
    
    # Try WASAPI loopback via -f waveout
    result2 = subprocess.run(
        [ffmpeg_path, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
        capture_output=True, text=True, timeout=10
    )
    print("\n=== Full dshow output ===")
    for line in result2.stderr.split('\n'):
        if 'dshow' in line.lower() or 'device' in line.lower() or 'alternative' in line.lower():
            print(line)
            
except Exception as e:
    print("Error:", e)
