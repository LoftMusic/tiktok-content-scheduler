import sounddevice as sd

print("Default Output:", sd.query_devices(kind="output"))
print("Default Input:", sd.query_devices(kind="input"))
