# Get current output
$current = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Multimedia\Sound Mapper' -Name 'Playback' -ErrorAction SilentlyContinue
Write-Host "Current default: $($current.Playback)"

# List PnP audio devices
Write-Host "`nAvailable audio devices:"
Get-PnpDevice -Class AudioEndpoint -Status OK | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize
