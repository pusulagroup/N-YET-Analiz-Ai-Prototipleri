#!/bin/bash
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then
  exec python3 run_v14_4_2.py
elif command -v python >/dev/null 2>&1; then
  exec python run_v14_4_2.py
else
  echo "[HATA] Python 3 bulunamadi."
  read -r -p "Kapatmak icin Enter..."
  exit 1
fi
