import sys
sys.path.insert(0, r'C:\Users\Studio3\AppData\Roaming\Python\Python311\site-packages')
try:
    import sounddevice as sd
    print(f"sounddevice: {sd}")
    print(f"PortAudio version: {sd.get_portaudio_version()}")
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
