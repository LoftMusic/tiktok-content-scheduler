Get-WmiObject Win32_SoundDevice | ForEach-Object { if ($_.Name -match "Universal") { $_ | Select-Object Name, DeviceID } }
