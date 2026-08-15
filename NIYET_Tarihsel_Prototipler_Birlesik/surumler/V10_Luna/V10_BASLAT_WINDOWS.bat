@echo off
cd /d "%~dp0"
title NIYET V10 Luna
py -3 run_v10.py
if errorlevel 1 python run_v10.py
pause
