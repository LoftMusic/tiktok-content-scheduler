# Switch Audio Devices using AudioDeviceCmdlets
# Works!

Import-Module AudioDeviceCmdlets

# Get current devices
$currentPlayback = Get-AudioDevice -Playback
$currentRecording = Get-AudioDevice -Recording

Write-Host "Before:"
Write-Host "  Playback: $($currentPlayback.Name)"
Write-Host "  Recording: $($currentRecording.Name)"

# Save original IDs
$originalPlaybackId = $currentPlayback.ID
$originalRecordingId = $currentRecording.ID

# VAC indices
# VAC Playback: Index 2
# VAC Recording: Index 5

Write-Host "`nSwitching to VAC..."

# Switch playback to VAC (Index 2)
Set-AudioDevice -Index 2
Write-Host "  Playback -> VAC"

# Switch recording - use Set-AudioDevice without -Recording, 
# we need to set the default recording device differently
# Let's check what index 5 is
$recDevice = Get-AudioDevice -List | Where-Object { $_.Index -eq 5 }
Write-Host "  Recording device at index 5: $($recDevice.Name)"

# Try setting recording using Index
Set-AudioDevice -Index 5
Write-Host "  Recording -> Index 5"

# Wait a bit
Start-Sleep -Milliseconds 500

# Verify
$newPlayback = Get-AudioDevice -Playback
$newRecording = Get-AudioDevice -Recording

Write-Host "`nAfter:"
Write-Host "  Playback: $($newPlayback.Name)"
Write-Host "  Recording: $($newRecording.Name)"

# Output original IDs for restore
Write-Output "ORIGINAL:$originalPlaybackId|$originalRecordingId"
