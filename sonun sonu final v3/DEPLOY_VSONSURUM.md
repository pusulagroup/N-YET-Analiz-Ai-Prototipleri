# NİYET VFINAL2 — GitHub / Render Dağıtımı

## GitHub güncellemesi
1. `VFINAL2_GITHUB_GUNCELLEME.zip` dosyasını açın.
2. İçeriği mevcut `niyet-v16` repo köküne kopyalayın; aynı adlı dosyaları değiştirin.
3. Mevcut `videos/` klasörünü silmeyin veya değiştirmeyin.
4. GitHub Desktop'ta değişiklikleri kontrol edin.
5. Önerilen commit mesajı: `VFINAL2 final feature and UX calibration`
6. Commit ve Push origin yapın.

## Render
Mevcut web servisinin çalışma giriş noktası korunur.

Build Command:
`pip install -r requirements.txt`

Start Command:
`gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 240 app_v16_2:app`

Push sonrası otomatik deploy açıksa deploy'u bekleyin. Değilse Render > Manual Deploy > Deploy latest commit kullanın.

## Deploy sonrası minimum kontrol
- `/healthz`
- `/robots.txt`
- `/sitemap.xml`
- Ana akış / profil / sohbet / skorum / gelişim ekranları
- Soru örneği: `bu proje mi geçecekmiş?` + Soru
- Açık hakaret örneği: `sen aptalsın`
- Sohbet üç nokta menüsü ve geri alma işlemleri
- Görsel ekli normal AI bot sohbeti
- Engellenen kişinin akıştan kaybolması
- Yeniden paylaşımın profilde görünmesi
