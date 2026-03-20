@echo off
echo ========================================
echo Auto-Switch Sample Recorder
echo ========================================
echo.
echo Usage:
echo   auto_record.bat           - Manual recording (press Enter to stop)
echo   auto_record.bat 10       - Record for 10 seconds
echo.
if "%1"=="" (
    powershell -ExecutionPolicy Bypass -File "%~dp0auto_record.ps1"
) else (
    powershell -ExecutionPolicy Bypass -File "%~dp0auto_record.ps1" -RecordDuration %1
)
