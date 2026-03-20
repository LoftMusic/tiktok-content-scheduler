$ErrorActionPreference = 'Continue'
$errLog = 'C:\Users\Studio3\Desktop\app_verbose_err.log'
$outLog = 'C:\Users\Studio3\Desktop\app_verbose_out.log'

# Start the app
$p = Start-Process 'C:\Users\Studio3\.openclaw\workspace\splice-desktop\dist\win-unpacked\Splice Desktop Recorder.exe' -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog

# Wait for app to initialize
Start-Sleep 3

# Check if still running
if ($p.HasExited) {
    Write-Host "App exited early with code: $($p.ExitCode)"
    Get-Content $errLog -ErrorAction SilentlyContinue | Select-Object -First 20
    exit
}

Write-Host "App is running, PID: $($p.Id)"
Write-Host "Press Enter to stop the app..."
Read-Host

# Stop the app
Stop-Process $p.Id -Force -ErrorAction SilentlyContinue

# Show the logs
Write-Host "`n=== STDERR LOG ===" 
Get-Content $errLog -ErrorAction SilentlyContinue | Select-Object -First 40
Write-Host "`n=== STDOUT LOG ===" 
Get-Content $outLog -ErrorAction SilentlyContinue | Select-Object -First 20
