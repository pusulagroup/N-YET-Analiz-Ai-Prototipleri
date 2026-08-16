@echo off
cd /d "%~dp0"
title NIYET V13 - Algi Kararliligi ve Minimum Mudahale
py -3 run_v13.py
if errorlevel 1 python run_v13.py
pause
