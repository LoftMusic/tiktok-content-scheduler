Import-Module AudioDeviceCmdlets

Get-AudioDevice -List | Where-Object { $_.Name -match "Virtual" } | Format-Table Name, Index, ID
