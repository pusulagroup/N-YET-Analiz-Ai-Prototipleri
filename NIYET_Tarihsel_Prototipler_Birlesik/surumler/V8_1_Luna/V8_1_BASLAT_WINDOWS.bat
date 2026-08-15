@echo off
cd /d "%~dp0"
echo NİYET V8.1 Luna baslatiliyor - http://127.0.0.1:8818
py run_v8.py 2>nul || python run_v8.py
pause
