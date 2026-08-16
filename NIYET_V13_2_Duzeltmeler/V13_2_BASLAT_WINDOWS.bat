@echo off
cd /d "%~dp0"
title NIYET V13.2 - Merkezi Skor ve Guvenlik
py -3 run_v13.py
if errorlevel 1 python run_v13.py
pause
