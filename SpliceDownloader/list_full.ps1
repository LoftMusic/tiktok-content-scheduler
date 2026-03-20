Import-Module AudioDeviceCmdlets

Write-Host "=== All Devices with Full Info ==="
Get-AudioDevice -List | Format-List Name, Index, ID, Type, Direction
