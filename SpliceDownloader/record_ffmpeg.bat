@echo off
echo Recording with ffmpeg (WASAPI loopback)...
echo Press Ctrl+C to stop

set timestamp=%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

"C:\Users\ASU\.openclaw\workspace\SpliceDownloader\ffmpeg\ffmpeg.exe" -f wasapi -i audio="Line 1 (Virtual Audio Cable)" -y "C:\Users\ASU\.openclaw\workspace\SpliceDownloader\recording_%timestamp%.wav"

echo Recording saved!
pause
