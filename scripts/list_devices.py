import sounddevice as sd

print("Available audio devices:")
print("=" * 60)
for i, d in enumerate(sd.query_devices()):
    print(f"{i}: {d['name']}")
    print(f"   Input channels: {d['max_input_channels']}, Output channels: {d['max_output_channels']}")
    print()