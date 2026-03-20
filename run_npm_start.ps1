$ErrorActionPreference = 'Continue'
$start = Get-Date
$proc = Start-Process 'C:\Users\Studio3\.openclaw\workspace\splice-desktop\node_modules\.bin\electron.cmd' -ArgumentList 'C:\Users\Studio3\.openclaw\workspace\splice-desktop' -PassThru -NoNewWindow -RedirectStandardError 'C:\Users\Studio3\Desktop\npm_start_err.log' -RedirectStandardOutput 'C:\Users\Studio3\Desktop\npm_start_out.log'
Start-Sleep 3
# Kill the process
if (!$proc.HasExited) { 
    Stop-Process $proc.Id -Force -ErrorAction SilentlyContinue 
}
Write-Host "--- STDERR ---"
Get-Content 'C:\Users\Studio3\Desktop\npm_start_err.log' -ErrorAction SilentlyContinue | Select-Object -First 30
Write-Host "--- STDOUT ---"
Get-Content 'C:\Users\Studio3\Desktop\npm_start_out.log' -ErrorAction SilentlyContinue | Select-Object -First 30
