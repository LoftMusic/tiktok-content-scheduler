Get-WmiObject Win32_SoundDevice | ForEach-Object { if ($_.Name -match "Apollo") { $_.Name + " | " + $_.DeviceID } }
