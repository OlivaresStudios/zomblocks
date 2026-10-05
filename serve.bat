@echo off
rem Optional: serves public\ on http://localhost:8000 (the wiki also works by opening public\index.html)
cd /d "%~dp0public"
start http://localhost:8000/index.html
python -m http.server 8000
