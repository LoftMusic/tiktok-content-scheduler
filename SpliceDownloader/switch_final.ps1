Import-Module AudioDeviceCmdlets

# Check current
$p = Get-AudioDevice -Playback
$r = Get-AudioDevice -Recording

Write-Host "Before:"
Write-Host "  Playback: $($p.Name)"
Write-Host "  Recording: $($r.Name)"

# Switch
Set-AudioDevice -Index 2
Get-AudioDevice -List | Where-Object { $_.Index -eq 5 } | Set-AudioDevice

Start-Sleep -Milliseconds 300

# Check after
$p2 = Get-AudioDevice -Playback
$r2 = Get-AudioDevice -Recording

Write-Host "After:"
Write-Host "  Playback: $($p2.Name)"
Write-Host "  Recording: $($r2.Name)"
