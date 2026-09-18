# VFINAL2 · Final Düzeltme Paketi

## Son profesyonel düzeltmeler
- Açık hakaret/aşağılayıcı dil kısa yolu artık **nefret söylemi** olarak etiketlenmiyor. `aptal`, `salak`, `mal`, `davar` gibi kişiye yönelik ifadeler **Hakaret / Aşağılayıcı Dil** olarak sınıflandırılıyor; nefret söylemi terimi korunan gruplara yönelik saldırılar için ayrılıyor.
- Beğeni ve yeniden paylaşım sayıları **NİYET Skoru veya Saygı puanını artık hiçbir şekilde artırmıyor**. Sosyal etkileşim ile iletişim davranışı puanı birbirinden ayrıldı.
- AI servisi timeout/kota/ağ hatası yaşarsa ekran boş kalmıyor: **yerel ön analiz korunuyor ve kullanıcıya açık bir servis uyarısı gösteriliyor**. Derin analiz ve sohbet tarafında da anlaşılır tekrar-dene mesajı var.
- NİYET Skoru beş alanın eşit ağırlıklı (%20) aritmetik ortalaması olarak korunuyor.

# CHANGELOG — VFINAL2

Bu sürüm V YARIŞMA / R1 / SEO tabanının son kullanıcı geri bildirimlerine göre güncellenmiş final katmanıdır.

- İfade Önerisi yedeği: özellikle Soru niyetinde dolaylı-retorik soru sadeleştirmesi.
- Yerel hızlı güvenlik: belirli açık hakaret sözcüklerinde AI beklemeden uyarı + minimum düzeltme.
- NİYET Skoru: 5 alan × %20; genel skor = aritmetik ortalama.
- Skorum ekranı: daha büyük ve açıklayıcı genel skor/formül görünümü.
- Akış: 34/38/40 Tartışma Isısına sahip üç doğal örnek zincir.
- Header: VFINAL2 etiketi ve hizalama düzeltmesi.
- Sohbetler: favori/arşiv/engel, geri alma, sıralama, durum ikonları, hover ipuçları.
- Sohbetler: 5 başlangıç bot mesajı ve okunmamış sayaçları.
- Sohbet içi: görsel/dosya ekleme; görsel için multimodal AI yanıtı.
- Profil: yeniden paylaşımlar “Yeniden paylaşıldı” etiketiyle timeline'a eklenir.
- Etkileşim: 5 benzersiz beğeni/yeniden paylaşım başına +1 Saygı katkısı.
- Engelleme: engellenen kişinin gönderileri akıştan filtrelenir.
- Test botları: Tolga/Berk daha sert ama hakaretsiz; açık test botu etiketi.
- Altyapı: `app_v16_2:app` Render entrypoint, SEO ve video yolları korunmuştur.

## Çalıştırılabilir paket düzeltmesi
- `BASLAT_VFINAL2_WINDOWS.bat` ile tek tık yerel başlatma eklendi.
- Yerel başlatma Flask/Gunicorn kurulumundan bağımsız hale getirildi; Python 3 yeterli.
- `local_launcher.py` tarayıcıyı otomatik açar ve `.env.local` desteği sağlar.
- `run_v16_web.py` VFINAL2 sürüm etiketleriyle eşitlendi.
- Eski yerel test başlatıcıları yeni çalışan başlatıcıya yönlendirildi.
