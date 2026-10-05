@echo off
rem Rebuilds the wiki from the add-on (zombie_RP, zombie_BP, the guidebook data) into public\r
cd /d "%~dp0"
python toolsuild.py %*
if errorlevel 1 pause & exit /b 1
echo Open public\index.html (or serve.bat)
pause
