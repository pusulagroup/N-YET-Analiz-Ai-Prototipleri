# VFINAL2 — Render / GitHub Dağıtımı

VFINAL2 teknik sürüm adıdır; kullanıcı arayüzünde sürüm etiketi görünmez.

## GitHub
GitHub güncelleme ZIP'inin içeriğini mevcut repo köküne kopyalayın ve dosyaları değiştirin. Mevcut `videos/` klasörünü silmeyin.

Önerilen commit mesajı:
`VFINAL2 remove chat media and freeze final UX`

## Render
Build Command:
`pip install -r requirements.txt`

Start Command:
`gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 240 app_v16_2:app`

Deploy sonrası kontrol:
- `/`
- `/healthz`
- `/robots.txt`
- `/sitemap.xml`
- normal metin tabanlı sohbet
- gönderi analizi ve servis fallback davranışı

Sohbet medya yükleme özelliği bu sürümde kasıtlı olarak yoktur.
