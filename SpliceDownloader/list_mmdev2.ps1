# List all MMDEVAPI audio devices with names
$renderPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render"

if (Test-Path $renderPath) {
    $devices = Get-ChildItem $renderPath
    foreach ($key in $devices) {
        $propsPath = "$renderPath\$($key.PSChildName)\Properties"
        if (Test-Path $propsPath) {
            $props = Get-ItemProperty $propsPath
            if ($props.DeviceDesc) {
                $desc = $props.DeviceDesc -replace '.*,', ''
                $id = "SWD\MMDEVAPI\$($key.PSChildName)"
                Write-Host "$desc"
                Write-Host "  ID: $id"
                Write-Host ""
            }
        }
    }
}
