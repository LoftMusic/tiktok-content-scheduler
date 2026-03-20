# Switch Audio Devices using AudioDeviceCmdlets
# This is more reliable than registry

Import-Module AudioDeviceCmdlets

# Get current devices
$currentPlayback = Get-AudioDevice -Playback
$currentRecording = Get-AudioDevice -Recording

Write-Host "Current Playback: $($currentPlayback.Name)"
Write-Host "Current Recording: $($currentRecording.Name)"

# Find VAC playback device
$vacPlayback = Get-AudioDevice -List | Where-Object { $_.Name -match "Virtual Audio Cable" -and $_.Direction -eq "Playback" }
$vacRecording = Get-AudioDevice -List | Where-Object { $_.Name -match "Virtual Audio Cable" -and $_.Direction -eq "Recording" }

Write-Host "`nVAC Playback: $($vacPlayback.Name) (Index: $($vacPlayback.Index))"
Write-Host "VAC Recording: $($vacRecording.Name) (Index: $($vacRecording.Index))"

# Save original devices
$originalPlaybackId = $currentPlayback.ID
$originalRecordingId = $currentRecording.ID

Write-Host "`nSaving original devices..."
Write-Host "Original Playback ID: $originalPlaybackId"
Write-Host "Original Recording ID: $originalRecordingId"

# Switch to VAC
Write-Host "`nSwitching to VAC..."

if ($vacPlayback) {
    Set-AudioDevice -Index $vacPlayback.Index
    Write-Host "Playback switched to: $($vacPlayback.Name)"
}

if ($vacRecording) {
    Set-AudioDevice -Index $vacRecording.Index -Recording
    Write-Host "Recording switched to: $($vacRecording.Name)"
}

# Verify
$newPlayback = Get-AudioDevice -Playback
$newRecording = Get-AudioDevice -Recording

Write-Host "`nAfter switch:"
Write-Host "Playback: $($newPlayback.Name)"
Write-Host "Recording: $($newRecording.Name)"
