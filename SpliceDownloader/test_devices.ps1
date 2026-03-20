Get-WmiObject Win32_SoundDevice | ForEach-Object { if ($_.Name -match "Virtual") { $_ | Select-Object Name, DeviceID } }
