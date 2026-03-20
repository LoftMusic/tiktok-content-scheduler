# List all MMDEVAPI audio devices
$renderPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render"

if (Test-Path $renderPath) {
    Get-ChildItem $renderPath | ForEach-Object {
        $key = $_
        $props = Get-ItemProperty "$renderPath\$($key.PSChildName)\Properties"
        $name = ($props.DeviceDesc -split ';')[-1]
        $id = "SWD\MMDEVAPI\$($key.PSChildName)"
        Write-Host "$name"
        Write-Host "  ID: $id"
        Write-Host ""
    }
}
