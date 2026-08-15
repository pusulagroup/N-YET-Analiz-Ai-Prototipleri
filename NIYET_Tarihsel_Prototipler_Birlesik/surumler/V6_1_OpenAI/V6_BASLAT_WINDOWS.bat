@echo off
cd /d %~dp0
py run_v6.py
if errorlevel 1 python run_v6.py
pause
