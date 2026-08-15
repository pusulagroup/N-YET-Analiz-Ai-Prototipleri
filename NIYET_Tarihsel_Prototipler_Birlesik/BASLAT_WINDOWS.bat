@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py launcher.py
) else (
  python launcher.py
)
if errorlevel 1 (
  echo.
  echo Python bulunamadi veya baslatici calistirilamadi.
  echo Python 3 kurulu oldugunu kontrol edin.
  pause
)
