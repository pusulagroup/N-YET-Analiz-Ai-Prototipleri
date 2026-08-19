@echo off
chcp 65001 >nul
cd /d "%~dp0"
pip install -r requirements.txt
set FLASK_APP=app_vyarisma.py
python -m flask run --host=127.0.0.1 --port=10000
pause
