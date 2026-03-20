@echo off
echo ========================================
echo VST Extractor for BANDA CORRIDOS
echo ========================================
echo.
cd /d "%~dp0"
echo Choose extraction mode:
echo   1. All Notes (C-1 to G8) - single folder
echo   2. All Presets with all notes
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" goto notes
if "%choice%"=="2" goto presets

:notes
echo.
echo Starting Note Extractor...
python vst_full_extractor.py
goto end

:presets
echo.
echo Starting Preset Extractor...
python vst_preset_extractor.py
goto end

:end
echo.
echo ========================================
echo Done! Check output folder.
echo ========================================
pause
