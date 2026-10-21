@echo off
cd /d "%~dp0"
python scripts\build.py
if errorlevel 1 (
  echo Build failed. Check content.json for valid JSON syntax.
  pause
  exit /b 1
)
start "" "%~dp0dist\index.html"
echo Done. Refresh your browser after each rebuild.
pause
