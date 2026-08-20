@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title NIYET VSONSURUM
echo ==========================================================
echo   NIYET VSONSURUM - TEK TIK YEREL BASLATICI
echo ==========================================================
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 local_launcher.py
  goto done
)
where python >nul 2>&1
if %errorlevel%==0 (
  python local_launcher.py
  goto done
)
echo [HATA] Python 3 bulunamadi.
echo Python 3 kurulduktan sonra bu dosyayi tekrar acin.
echo https://www.python.org/downloads/
:done
echo.
echo Sunucu kapandi.
pause
