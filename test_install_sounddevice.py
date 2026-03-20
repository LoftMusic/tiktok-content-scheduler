import subprocess, sys

pip_path = r"C:\Users\Studio3\AppData\Roaming\Python\Python311\Scripts\pip3.11.exe"
print("Installing sounddevice, numpy, soundfile via pip...")
result = subprocess.run(
    [pip_path, "install", "sounddevice", "numpy", "soundfile", "-q"],
    capture_output=True, text=True, timeout=180
)
print("Return code:", result.returncode)
print("STDOUT:", result.stdout[-1000:] if result.stdout else "(empty)")
print("STDERR:", result.stderr[-1000:] if result.stderr else "(empty)")

if result.returncode == 0:
    print("\nTesting sounddevice import...")
    try:
        import sounddevice as sd
        print(f"sounddevice {sd.version}")
        devs = sd.query_devices()
        print(f"Devices:\n{devs}")
        loopback = [d for d in devs if 'loopback' in d.get('name','').lower()]
        print(f"\nLoopback devices: {loopback}")
    except Exception as e:
        print(f"Error: {e}")
