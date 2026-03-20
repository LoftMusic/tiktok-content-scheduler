import sys
sys.path.insert(0, r'C:\Users\Studio3\AppData\Roaming\Python\Python311\site-packages')
import sounddevice as sd

# Test each candidate device
test_devices = [29, 0, 1, 2]  # Stereo Mix, Sound Mapper, Volt, SoundGrid

for dev_idx in test_devices:
    print(f"\n=== Testing device {dev_idx} ===")
    try:
        info = sd.query_devices(dev_idx)
        print(f"Device: {info['name']}")
        print(f"  max_inputs={info.get('max_input_channels')}, max_outputs={info.get('max_output_channels')}")
        print(f"  default_sr={info.get('default_samplerate')}, hostapi={info.get('hostapi')}")
        
        # Try opening a stream
        print(f"  Trying to open stream...")
        stream = sd.InputStream(
            device=dev_idx,
            samplerate=44100,
            channels=min(info.get('max_input_channels', 2), 2),
            dtype='float32',
            latency='high'
        )
        stream.start()
        import time
        time.sleep(0.5)
        data, overflowed = stream.read(4410)
        stream.stop()
        stream.close()
        print(f"  SUCCESS: got {data.shape}, max_amp={abs(data).max():.4f}")
    except Exception as e:
        print(f"  ERROR: {e}")
