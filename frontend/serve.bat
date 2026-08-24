@echo off
REM Romio Cafe & Restaurant — start a local preview server.
REM Double-click this file, then open http://localhost:8000/ in your browser.
cd /d "%~dp0"
echo.
echo   Romio Cafe ^& Restaurant — local preview
echo   ---------------------------------------
echo   Serving this folder at:  http://localhost:8000/
echo   Press Ctrl+C in this window to stop.
echo.
python -m http.server 8000
pause
