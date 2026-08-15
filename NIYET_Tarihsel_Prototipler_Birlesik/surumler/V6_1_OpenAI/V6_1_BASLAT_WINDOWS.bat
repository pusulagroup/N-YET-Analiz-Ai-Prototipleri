@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py run_v6.py
) else (
  python run_v6.py
)
pause
