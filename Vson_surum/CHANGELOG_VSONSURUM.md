# CHANGELOG — VSONSURUM

Bu sürüm V YARIŞMA / R1 / SEO tabanının son kullanıcı geri bildirimlerine göre güncellenmiş final katmanıdır.

- İfade Önerisi yedeği: özellikle Soru niyetinde dolaylı-retorik soru sadeleştirmesi.
- Yerel hızlı güvenlik: belirli açık hakaret sözcüklerinde AI beklemeden uyarı + minimum düzeltme.
- NİYET Skoru: 5 alan × %20; genel skor = aritmetik ortalama.
- Skorum ekranı: daha büyük ve açıklayıcı genel skor/formül görünümü.
- Akış: 34/38/40 Tartışma Isısına sahip üç doğal örnek zincir.
- Header: VSONSURUM etiketi ve hizalama düzeltmesi.
- Sohbetler: favori/arşiv/engel, geri alma, sıralama, durum ikonları, hover ipuçları.
- Sohbetler: 5 başlangıç bot mesajı ve okunmamış sayaçları.
- Sohbet içi: görsel/dosya ekleme; görsel için multimodal AI yanıtı.
- Profil: yeniden paylaşımlar “Yeniden paylaşıldı” etiketiyle timeline'a eklenir.
- Etkileşim: 5 benzersiz beğeni/yeniden paylaşım başına +1 Saygı katkısı.
- Engelleme: engellenen kişinin gönderileri akıştan filtrelenir.
- Test botları: Tolga/Berk daha sert ama hakaretsiz; açık test botu etiketi.
- Altyapı: `app_v16_2:app` Render entrypoint, SEO ve video yolları korunmuştur.

## Çalıştırılabilir paket düzeltmesi
- `BASLAT_VSONSURUM_WINDOWS.bat` ile tek tık yerel başlatma eklendi.
- Yerel başlatma Flask/Gunicorn kurulumundan bağımsız hale getirildi; Python 3 yeterli.
- `local_launcher.py` tarayıcıyı otomatik açar ve `.env.local` desteği sağlar.
- `run_v16_web.py` VSONSURUM sürüm etiketleriyle eşitlendi.
- Yerel yedek sunucuya `robots.txt`, `sitemap.xml` ve görsel sohbet (`/api/chat_media`) desteği eklendi.
- Görsel sohbet için yerel istek boyutu sınırı 6 MB'a çıkarıldı.
- Eski yerel test başlatıcıları yeni çalışan başlatıcıya yönlendirildi.
