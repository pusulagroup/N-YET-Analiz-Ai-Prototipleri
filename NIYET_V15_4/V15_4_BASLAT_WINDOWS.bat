@echo off
chcp 65001 >nul
cd /d "%~dp0"
python run_v15_4.py
if errorlevel 1 py -3 run_v15_4.py
pause
