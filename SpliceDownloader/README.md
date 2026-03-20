# Audio Recorder

## Extension (Chrome)
Click icon to record audio from tab. Downloads as .webm

## Python Script (Recommended)
For auto-trim silence, use: `record_trim.py`

### Requirements:
```
pip install sounddevice numpy scipy
```

### Run:
```
python record_trim.py
```

### Settings (edit in file):
- SILENCE_THRESHOLD = 0.02
- MIN_SOUND_DURATION = 0.1s
- MIN_SILENCE_GAP = 0.3s

The script automatically:
1. Records audio
2. Detects sound segments
3. Removes silence
4. Exports each sample as separate .wav file
