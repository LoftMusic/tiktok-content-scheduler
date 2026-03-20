Import-Module AudioDeviceCmdlets

Write-Host "=== Default Playback ==="
Get-AudioDevice -Playback

Write-Host "`n=== Default Recording ==="  
Get-AudioDevice -Recording

Write-Host "`n=== All Devices ==="
Get-AudioDevice -List | Format-Table Name, Index, Direction
