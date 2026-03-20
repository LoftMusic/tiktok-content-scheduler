# List all playback devices with their IDs
Get-WmiObject Win32_SoundDevice | Where-Object {$_.Name -match "Audio|Cable|Speaker"} | Select-Object Name, DeviceID
