$p = Start-Process 'C:\Users\Studio3\.openclaw\workspace\splice-desktop\dist\win-unpacked\Splice Desktop Recorder.exe' -PassThru -RedirectStandardError 'C:\Users\Studio3\Desktop\app_err.log'
Start-Sleep 5
if (!$p.HasExited) {
    Write-Host 'App still running after 5s - killing...'
    Stop-Process $p.Id -Force -ErrorAction SilentlyContinue
}
if (Test-Path 'C:\Users\Studio3\Desktop\app_err.log') {
    Get-Content 'C:\Users\Studio3\Desktop\app_err.log'
}
