# Switch Audio Devices using AudioDeviceCmdlets
# More reliable than registry

Import-Module AudioDeviceCmdlets

# Get current devices
$currentPlayback = Get-AudioDevice -Playback
$currentRecording = Get-AudioDevice -Recording

Write-Host "Current Playback: $($currentPlayback.Name)"
Write-Host "Current Recording: $($currentRecording.Name)"

# Save original device IDs
$originalPlaybackId = $currentPlayback.ID
$originalRecordingId = $currentRecording.ID

# VAC indices (found from list_full.ps1)
# VAC Playback: Index 2
# VAC Recording: Index 5

Write-Host "`nSwitching to VAC..."

# Switch playback to VAC (Index 2)
Set-AudioDevice -Index 2
Write-Host "Playback -> Line 1 (Virtual Audio Cable)"

# Switch recording to VAC (Index 5)  
Set-AudioDevice -Index 5 -Recording
Write-Host "Recording -> Line 1 (Virtual Audio Cable)"

# Verify
Start-Sleep -Milliseconds 500

$newPlayback = Get-AudioDevice -Playback
$newRecording = Get-AudioDevice -Recording

Write-Host "`n=== After Switch ==="
Write-Host "Playback: $($newPlayback.Name)"
Write-Host "Recording: $($newRecording.Name)"

# Save IDs for restore
Write-Output "$originalPlaybackId|$originalRecordingId"
