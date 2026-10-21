@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scripts\build.py
if errorlevel 1 (
  echo.
  echo Build failed. Check content.json or README_修改说明.md.
  pause
  exit /b 1
)
start "" "%~dp0dist\index.html"
echo.
echo Done. Refresh your browser after each rebuild.
pause
