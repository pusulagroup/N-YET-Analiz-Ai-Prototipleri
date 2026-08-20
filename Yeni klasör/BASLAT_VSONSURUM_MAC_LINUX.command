#!/bin/bash
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then
  exec python3 local_launcher.py
elif command -v python >/dev/null 2>&1; then
  exec python local_launcher.py
else
  echo "[HATA] Python 3 bulunamadı."
  read -r -p "Kapatmak için Enter..." _
  exit 1
fi
