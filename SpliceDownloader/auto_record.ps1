# Auto-Switch Recorder - Universal Edition
# Automatically switches BOTH output AND input to VAC for recording, then restores original devices

param(
    [int]$RecordDuration = 0,  # 0 = manual stop, otherwise seconds
    [string]$OutputDir = "."
)

$ErrorActionPreference = "Stop"

# Registry path for Sound Mapper
$regPath = 'HKCU:\Software\Microsoft\Multimedia\Sound Mapper'

# Function to refresh Windows audio
function Refresh-Audio {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Audio {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern void SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
    public const int HWND_BROADCAST = 0xffff;
    public const int WM_SETTINGCHANGE = 0x001A;
    public static void Refresh() {
        UIntPtr result;
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Audio", 2, 1000, out result);
    }
}
"@
    [Audio]::Refresh()
}

# Get current output and input devices
$originalOutput = (Get-ItemProperty -Path $regPath -Name 'Playback' -ErrorAction SilentlyContinue).Playback
$originalInput = (Get-ItemProperty -Path $regPath -Name 'Record' -ErrorAction SilentlyContinue).Playback

if (-not $originalOutput) { $originalOutput = "" }
if (-not $originalInput) { $originalInput = "" }

# Find Virtual Audio Cable ID from registry
$vacPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render"
$vacID = $null

if (Test-Path $vacPath) {
    $devices = Get-ChildItem $vacPath
    foreach ($key in $devices) {
        $propsPath = "$vacPath\$($key.PSChildName)\Properties"
        if (Test-Path $propsPath) {
            $props = Get-ItemProperty $propsPath
            if ($props.DeviceDesc -match "Virtual Audio Cable") {
                $vacID = "SWD\MMDEVAPI\$($key.PSChildName)"
                break
            }
        }
    }
}

if (-not $vacID) {
    # Fallback ID from existing script
    $vacID = "SWD\MMDEVAPI\{0.0.1.00000000}.{9C8A1CEB-0B21-4211-9FBB-CDF8D4F02824}"
}

Write-Host "========================================"
Write-Host "Auto-Switch Sample Recorder"
Write-Host "========================================"
Write-Host ""
Write-Host "Original output: $(if($originalOutput){$originalOutput}else{'System Default'})"
Write-Host "Original input: $(if($originalInput){$originalInput}else{'System Default'})"
Write-Host "VAC ID: $vacID"
Write-Host ""

# Switch BOTH to VAC
Write-Host "Switching output AND input to Virtual Audio Cable..."
Set-ItemProperty -Path $regPath -Name 'Playback' -Value $vacID -ErrorAction SilentlyContinue
Set-ItemProperty -Path $regPath -Name 'FrontBack' -Value $vacID -ErrorAction SilentlyContinue
Set-ItemProperty -Path $regPath -Name 'Record' -Value $vacID -ErrorAction SilentlyContinue
Refresh-Audio
Start-Sleep -Milliseconds 500
Write-Host "Done. Output and Input are now VAC."
Write-Host ""

# Run recording
Write-Host "Starting recording..."
Write-Host "PLAY AUDIO NOW!"
Write-Host ""

if ($RecordDuration -gt 0) {
    # Timed recording
    $pythonCode = @"
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time
import os

SAMPLE_RATE = 44100
CHANNELS = 2
DURATION = $RecordDuration

print(f'Recording for {DURATION} seconds...')
recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
sd.wait()

max_vol = np.max(np.abs(recording))
print(f'Max volume: {max_vol:.4f}')

if max_vol > 0.001:
    filename = f'auto_rec_{int(time.time())}.wav'
    wavfile.write(filename, SAMPLE_RATE, (recording * 32767).astype(np.int16))
    print(f'Saved: {filename}')
else:
    print('No audio detected!')
"@
    python -c $pythonCode
} else {
    # Manual recording - run the trim script
    python record_trim.py
}

# Restore original output and input
Write-Host ""
Write-Host "Restoring original devices..."

if ($originalOutput -and $originalOutput -ne "") {
    Set-ItemProperty -Path $regPath -Name 'Playback' -Value $originalOutput -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $regPath -Name 'FrontBack' -Value $originalOutput -ErrorAction SilentlyContinue
    Write-Host "Restored output to: $originalOutput"
}

if ($originalInput -and $originalInput -ne "") {
    Set-ItemProperty -Path $regPath -Name 'Record' -Value $originalInput -ErrorAction SilentlyContinue
    Write-Host "Restored input to: $originalInput"
}

if (-not $originalOutput) {
    Write-Host "No original output to restore (was using system default)"
}
if (-not $originalInput) {
    Write-Host "No original input to restore (was using system default)"
}

Refresh-Audio

Write-Host ""
Write-Host "========================================"
Write-Host "Done! Devices restored."
Write-Host "========================================"
