from __future__ import annotations

import atexit
import html
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSIONS = ROOT / "surumler"
HOST = "127.0.0.1"
CATALOG_PORT = int(os.getenv("NIYET_HISTORY_PORT", "8870"))

# Historical files are kept intact. The launcher only assigns unique runtime ports.
CONFIG = {
    "v1": {"label": "V1 · İlk Prototip", "kind": "static", "dir": "V1_Ilk_Prototip", "note": "İlk arayüz/prototip aşaması."},
    "v2": {"label": "V2 · Prototip", "kind": "static", "dir": "V2_Prototip", "note": "İlk prototipin genişletilmiş sürümü."},
    "v3": {"label": "V3 · Prototip", "kind": "static", "dir": "V3_Prototip", "note": "Arayüz ve özellik gelişiminin sonraki adımı."},
    "v4": {"label": "V4 · Prototip", "kind": "static", "dir": "V4_Prototip", "note": "Tarihsel prototip anlık görüntüsü."},
    "v5": {"label": "V5 · Prototip", "kind": "static", "dir": "V5_Prototip", "note": "Sunucu tabanlı sürümlere geçiş öncesi prototip."},
    "v6_1": {"label": "V6.1 · OpenAI", "kind": "python", "dir": "V6_1_OpenAI", "script": "run_v6.py", "port": 8806, "note": "Python backend ve OpenAI bağlantılı sürüm."},
    "v7": {"label": "V7 · Luna", "kind": "python", "dir": "V7_Luna", "script": "run_v7.py", "port": 8807, "note": "Luna tabanlı geliştirme aşaması."},
    "v8_1": {"label": "V8.1 · Luna", "kind": "python", "dir": "V8_1_Luna", "script": "run_v8.py", "port": 8818, "note": "Sosyal etkileşim ve skor sisteminin genişletildiği sürüm."},
    "v9": {"label": "V9 · Luna", "kind": "python", "dir": "V9_Luna", "script": "run_v9.py", "port": 8819, "note": "Luna analiz akışının ileri prototipi."},
    "v10": {"label": "V10 · Luna", "kind": "python", "dir": "V10_Luna", "script": "run_v10.py", "port": 8820, "note": "Güvenlik ve sosyal yapay zekâ özelliklerinin genişletildiği sürüm."},
    "v11": {"label": "V11 · Anket Entegre", "kind": "python", "dir": "V11_Anket_Entegre", "script": "run_v11.py", "port": 8830, "note": "İnsan algısı araştırması ve kalibrasyon entegrasyonu."},
    "v12_3": {"label": "V12.3 · TEKNOFEST Ana Tema", "kind": "python", "dir": "V12_3_Teknofest_AnaTema", "script": "run_v11.py", "port": 8843, "note": "TEKNOFEST görsel teması ve insan-kalibre NİYET motoru."},
}

PROCS: dict[str, subprocess.Popen] = {}
LOCK = threading.Lock()


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex((HOST, port)) == 0


def launch_python(key: str, cfg: dict) -> tuple[bool, str]:
    folder = VERSIONS / cfg["dir"]
    script = folder / cfg["script"]
    port = int(cfg["port"])
    if not script.exists():
        return False, f"Başlatma dosyası bulunamadı: {script.name}"

    if port_open(port):
        return True, f"http://{HOST}:{port}/"

    with LOCK:
        old = PROCS.get(key)
        if old and old.poll() is None:
            return True, f"http://{HOST}:{port}/"
        env = os.environ.copy()
        env["NIYET_PORT"] = str(port)
        # Preserve OPENAI_API_KEY if the user has set it in their environment.
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
        proc = subprocess.Popen(
            [sys.executable, script.name],
            cwd=str(folder),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        PROCS[key] = proc

    deadline = time.time() + 8
    while time.time() < deadline:
        if port_open(port):
            return True, f"http://{HOST}:{port}/"
        if proc.poll() is not None:
            return False, "Sürüm sunucusu başlatılamadı. Python kurulumunu kontrol edin."
        time.sleep(0.15)
    return False, "Sürüm başlatıldı ancak sunucu zamanında yanıt vermedi."


def stop_children() -> None:
    with LOCK:
        items = list(PROCS.items())
        PROCS.clear()
    for _, proc in items:
        if proc.poll() is not None:
            continue
        try:
            if os.name == "nt":
                proc.terminate()
            else:
                proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


atexit.register(stop_children)


CSS = r"""
:root{font-family:Arial,Helvetica,sans-serif;color:#10213e;background:#f3f6fb}
*{box-sizing:border-box}body{margin:0}.top{background:linear-gradient(110deg,#092a63,#0d47a1 68%,#cf2432);color:#fff;padding:28px 24px;border-bottom:5px solid #f4c430}.wrap{max-width:1120px;margin:0 auto}.top h1{margin:0 0 8px;font-size:30px}.top p{margin:0;opacity:.92;line-height:1.5}.notice{margin:24px auto 12px;background:#fff;border:1px solid #d8e1ef;border-radius:16px;padding:16px 18px;line-height:1.55;box-shadow:0 8px 24px rgba(10,35,80,.06)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;padding:12px 0 30px}.card{background:#fff;border:1px solid #d8e1ef;border-radius:16px;padding:18px;box-shadow:0 8px 24px rgba(10,35,80,.06);display:flex;flex-direction:column;min-height:190px}.badge{display:inline-block;background:#eaf2ff;color:#0d47a1;font-weight:700;padding:5px 9px;border-radius:999px;font-size:12px;width:max-content}.card h2{font-size:19px;margin:12px 0 7px}.card p{font-size:14px;line-height:1.5;color:#43536c;margin:0 0 18px}.actions{margin-top:auto;display:flex;gap:8px;align-items:center}.btn{display:inline-block;text-decoration:none;border:0;border-radius:10px;padding:10px 13px;font-weight:700;cursor:pointer;background:#cf2432;color:white}.btn.secondary{background:#0d47a1}.status{font-size:12px;color:#66758b}.footer{padding:0 0 35px;color:#66758b;font-size:13px}.err{color:#a11420;font-weight:700}@media(max-width:600px){.top h1{font-size:24px}.grid{grid-template-columns:1fr;padding-left:12px;padding-right:12px}.notice{margin-left:12px;margin-right:12px}}
"""


def catalog_html(message: str = "") -> str:
    cards = []
    for key, cfg in CONFIG.items():
        kind = cfg["kind"]
        if kind == "static":
            href = f"/static/{urllib.parse.quote(cfg['dir'])}/index.html"
            action = f'<a class="btn secondary" target="_blank" href="{href}">Sürümü Aç</a>'
            status = '<span class="status">Tek HTML · doğrudan açılır</span>'
        else:
            href = f"/launch?version={urllib.parse.quote(key)}"
            running = port_open(int(cfg["port"]))
            action = f'<a class="btn" target="_blank" href="{href}">{"Aç" if running else "Başlat ve Aç"}</a>'
            status = f'<span class="status">Port {cfg["port"]}{" · çalışıyor" if running else ""}</span>'
        cards.append(f'''<section class="card"><span class="badge">Tarihsel sürüm</span><h2>{html.escape(cfg['label'])}</h2><p>{html.escape(cfg['note'])}</p><div class="actions">{action}{status}</div></section>''')
    msg = f'<div class="notice err">{html.escape(message)}</div>' if message else ''
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NİYET · Tarihsel Prototipler</title><style>{CSS}</style></head><body><header class="top"><div class="wrap"><h1>NİYET · Tarihsel Prototipler</h1><p>Git öncesi ve önceki prototip sürümlerini tek klasörden incelemek için hazırlanmış yerel başlatıcı.</p></div></header><main class="wrap">{msg}<div class="notice"><strong>Not:</strong> Bu paket tarihsel sürüm dosyalarını yeniden yazmaz. Yalnızca her sürümü kendi gerekli dosyalarıyla birlikte saklar ve sunucu gerektiren sürümlere çakışmayan yerel portlar atayarak başlatır. OpenAI kullanan özellikler için sisteminizde ayrıca geçerli API erişimi gerekebilir.</div><div class="grid">{''.join(cards)}</div><div class="footer">Ana başlatıcı: http://{HOST}:{CATALOG_PORT}/ · Sunucuyu kapatmak için açılan terminal penceresini kapatabilirsiniz.</div></main></body></html>'''


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        pass

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            body = catalog_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        if path == "/launch":
            qs = urllib.parse.parse_qs(parsed.query)
            key = qs.get("version", [""])[0]
            cfg = CONFIG.get(key)
            if not cfg or cfg.get("kind") != "python":
                self.send_error(404, "Bilinmeyen sürüm"); return
            ok, target = launch_python(key, cfg)
            if ok:
                self.send_response(302); self.send_header("Location", target); self.end_headers(); return
            body = catalog_html(target).encode("utf-8")
            self.send_response(500); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path.startswith("/static/"):
            rel = urllib.parse.unquote(path[len("/static/"):]).lstrip("/")
            target = (VERSIONS / rel).resolve()
            try:
                target.relative_to(VERSIONS.resolve())
            except ValueError:
                self.send_error(403); return
            if target.is_dir():
                target = target / "index.html"
            if not target.exists() or not target.is_file():
                self.send_error(404); return
            ctype = self.guess_type(str(target))
            data = target.read_bytes()
            self.send_response(200); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        self.send_error(404)


def main() -> None:
    server = ThreadingHTTPServer((HOST, CATALOG_PORT), Handler)
    url = f"http://{HOST}:{CATALOG_PORT}/"
    print("NİYET Tarihsel Prototip Başlatıcı")
    print("Adres:", url)
    print("Kapatmak için Ctrl+C kullanın.")
    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        stop_children()

if __name__ == "__main__":
    main()
