# NİYET — VSONSURUM

TEKNOFEST yarışma kullanımı için V YARIŞMA tabanı korunarak hazırlanan son işlevsel sürümdür. Ana N'SOSYAL × NİYET arayüz yapısı, TEKNOFEST görsel dili, insan-algısı kalibrasyonu, eğitim videoları ve mevcut Render dağıtım mimarisi korunmuştur.

## Summary
NİYET VSONSURUM; ifade önerisi erişilebilirliğini, açık hakaret için beklemesiz güvenlik akışını, beş eşit ağırlıklı NİYET skorunu, daha anlaşılır skor ekranını, gelişmiş sohbet yönetimini, görsel destekli AI sohbetini, yeniden paylaşım profil akışını ve daha gerçekçi tartışma örneklerini tek final sürümde birleştirir.

## Temel değişiklikler
- Soru niyetinde retorik/dolaylı ifadeler için deterministik İfade Önerisi yedeği eklendi. Örnek: `bu proje mi geçecekmiş?` → `Bu proje geçecek mi?`.
- `aptal`, `salak`, `davar`, `mal`, `ahmak`, `gerizekalı` gibi açık hakaret sinyalleri ve bazı kişi ekli biçimleri dış AI analizini beklemeden güvenlik akışına alınır. `defol/git buradan` tek başına bu kısa yolu tetiklemez.
- Güvenlik sonucunun üstünde “Nefret söylemi tespit edildi. Bu mesajı paylaşmak istediğinizden emin misiniz?” uyarısı gösterilir; gerekçe ve minimum düzeltme de aynı modal içinde sunulur.
- Genel NİYET Skoru artık beş alanın aritmetik ortalamasıdır: Saygı, Yapıcılık, Tutarlılık, Gerilim Yönetimi ve İletişim Açıklığı; her alan %20 ağırlıktadır.
- Skor ekranında genel skor, alan adları, barlar ve formül açıklaması belirginleştirildi.
- Akışta üç normal paylaşımın Tartışma Isısı 34, 38 ve 40 seviyelerine getirildi; yorumlar daha sert ama hakaretsiz hale getirildi. Ek rozet eklenmedi.
- Sürüm etiketi `VSONSURUM` olarak güncellendi ve N'SOSYAL × NİYET başlığıyla dikey hizası düzeltildi.
- Sohbet satırlarına favori, arşiv ve engelle yönetimi eklendi; işlemler aynı üç nokta menüsünden geri alınabilir.
- Favoriler üste, arşivlenenler ve engellenenler alta taşınır. Engellenen kullanıcının paylaşımları akıştan kaldırılır.
- Beş sohbet kişisi başlangıçta mesaj göndermiş şekilde gelir ve okunmamış mesaj sayısı gösterilir.
- Sohbet satırı sağ düzeni: okunmamış sayısı → durum simgesi → üç nokta → Sohbet Sağlığı.
- Okunmamış sayısı, durum simgesi ve Sohbet Sağlığı için hover bilgi balonları eklendi.
- Mesaj alanına `+` menüsü, Görsel ekle ve Dosya ekle seçenekleri eklendi.
- Görsel ekleri normal AI botları Responses API görsel girdisiyle yorumlayabilir; görsel hassas özellik çıkarımı için kullanılmaz.
- Yeniden paylaşılan gönderiler Profil > Paylaşımlar içinde “Yeniden paylaşıldı” etiketiyle gösterilir.
- Her 5 benzersiz beğeni/yeniden paylaşım etkileşimi Saygı alanına +1 katkı sağlar.
- Tolga ve Berk “Sert konuşma tarzı test botu” olarak açıkça işaretlendi; yanıtları daha keskin hale getirildi ancak küfür/hakaret eklenmedi.
- SEO rotaları (`robots.txt`, `sitemap.xml`) ve mevcut domain/Render yapısı korunmuştur.

## Dağıtım
Render giriş noktası değiştirilmemiştir: `app_v16_2:app`.

Build Command:
`pip install -r requirements.txt`

Start Command:
`gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 240 app_v16_2:app`

## Not
`videos/` klasörü ve 25 mikro eğitim videosu bu sürümde içerik olarak değiştirilmemiştir. Tam paket arşivinde videolar dahildir; GitHub güncelleme paketi mevcut repo içindeki `videos/` klasörünü koruyacak şekilde hazırlanmıştır.

## Yerel çalıştırma — çalışan paket
ZIP'i **tamamen bir klasöre çıkardıktan sonra** Windows'ta `BASLAT_VSONSURUM_WINDOWS.bat` dosyasına çift tıklayın. Tarayıcı otomatik olarak `http://127.0.0.1:10000` adresini açar. Bu başlatıcı için Flask veya Gunicorn kurulması gerekmez; yalnızca Python 3 yeterlidir.

macOS/Linux için `BASLAT_VSONSURUM_MAC_LINUX.command` kullanılır.

Yerel AI özellikleri gerekiyorsa `.env.example` dosyasını `.env.local` olarak kopyalayıp `OPENAI_API_KEY` değerini yalnızca bu yerel dosyada tanımlayın. `.gitignore` nedeniyle `.env.local` GitHub'a eklenmez. Anahtar yokken arayüz, akış, skor, eğitimler ve yerel test özellikleri açılır; dış AI gerektiren istekler doğal olarak çalışmaz.

**Önemli:** `index.html` dosyasını doğrudan çift tıklayıp `file://` üzerinden açmayın. NİYET'in API ve video rotaları için yerel sunucu gerekir; bu nedenle başlatıcı dosyasını kullanın.
