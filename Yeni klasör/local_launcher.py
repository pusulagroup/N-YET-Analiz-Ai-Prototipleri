#!/usr/bin/env python3
"""NİYET VSONSURUM tek tık yerel başlatıcı (yalnızca Python 3 gerekir)."""
from __future__ import annotations
import os
import threading
import webbrowser
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load_env(path: Path):
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key,value=line.split("=",1)
        key=key.strip(); value=value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key]=value

load_env(ROOT/".env.local")
load_env(ROOT/".env")
os.environ.setdefault("HOST","127.0.0.1")
os.environ.setdefault("NIYET_PORT","10000")
os.environ.setdefault("NIYET_WEB_MODE","1")

# Ortam değişkenlerinden sonra import edilir.
import run_v16_web as core

URL="http://127.0.0.1:10000/"

if __name__=="__main__":
    print("="*60)
    print("NİYET VSONSURUM — YEREL ÇALIŞTIRMA")
    print("Adres:",URL)
    print("AI bağlantısı:","hazır" if core.API_KEY else "OPENAI_API_KEY tanımlı değil")
    if not core.API_KEY:
        print("Arayüz ve yerel özellikler açılır. AI için .env.local kullanın.")
        print(".env.local dosyasını GitHub'a yüklemeyin.")
    print("Kapatmak için Ctrl+C.")
    print("="*60)
    threading.Timer(1.0,lambda:webbrowser.open(URL,new=2)).start()
    core.main()
