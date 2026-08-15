@echo off
cd /d "%~dp0"
title NIYET V12.3 - Insan Kalibrasyonlu Luna
py -3 run_v11.py
if errorlevel 1 python run_v11.py
pause
