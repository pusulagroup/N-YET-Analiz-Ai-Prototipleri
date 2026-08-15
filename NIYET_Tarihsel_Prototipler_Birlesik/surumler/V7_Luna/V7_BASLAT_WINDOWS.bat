@echo off
cd /d "%~dp0"
py run_v7.py 2>nul || python run_v7.py
pause
