@echo off
chcp 65001 >nul
cd /d "%~dp0"
title NIYET V13.6 - API Baglanti Duzeltmesi

echo.
echo ==============================================
echo   NIYET V13.6 baslatiliyor...
echo ==============================================
echo.

where py >nul 2>&1
if %errorlevel%==0 goto use_py

where python >nul 2>&1
if %errorlevel%==0 goto use_python

where python3 >nul 2>&1
if %errorlevel%==0 goto use_python3

echo [HATA] Python bulunamadi.
echo Python 3 kurulu olmali. Kurulumdan sonra bu dosyayi yeniden ac.
echo.
pause
exit /b 1

:use_py
py -3 run_v13.py
goto finished

:use_python
python run_v13.py
goto finished

:use_python3
python3 run_v13.py
goto finished

:finished
if errorlevel 1 (
  echo.
  echo [HATA] NIYET sunucusu baslatilamadi.
  echo Yukaridaki hata mesajini ekran goruntusu olarak paylasabilirsin.
  echo.
  pause
)
