#!/bin/bash
cd "$(dirname "$0")"
pip3 install -r requirements.txt
FLASK_APP=app_vyarisma.py python3 -m flask run --host=127.0.0.1 --port=10000
