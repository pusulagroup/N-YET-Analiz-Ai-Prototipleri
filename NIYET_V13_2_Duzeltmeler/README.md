# NİYET V13.2 — Merkezi NİYET Skoru + Güvenlik Düzeltmeleri

V13.2, V13.1 üzerindeki kullanıcı testlerinde görülen döngü, güvenlik eşiği, Tartışma Isısı ve skor bütünlüğü sorunlarını düzeltir. Bu sürümde NİYET'in temel yaklaşımı korunur: sistem paylaşımı kullanıcı adına yönlendirmez; analiz eder, açıklar ve tavsiye sunar.

## Başlatma

### Windows
`V13_2_BASLAT_WINDOWS.bat`

### macOS / Linux
`V13_2_BASLAT_MAC_LINUX.command`

Varsayılan adres: `http://127.0.0.1:8847/`

OpenAI bağlantısı sunucu tarafında `OPENAI_API_KEY` ortam değişkeninden okunur. API anahtarı tarayıcı koduna veya repoya yazılmamalıdır.

## V13.2 ana değişiklikleri

### 1. Minimum Müdahale artık yalnızca tavsiye
- Öneri kartları metni otomatik değiştirmez.
- Öneri seçimi yeni bir analiz başlatmaz.
- Kullanıcı kendi ifadesini kendisi düzenler veya olduğu gibi paylaşır.
- Böylece öneri → yeniden analiz → yeni öneri döngüsü kaldırılmıştır.

### 2. Merkezi NİYET Skoru
Genel skorun beş alanı korunur:
- Saygı %25
- Yapıcılık %20
- Tutarlılık %20
- Gerilim Yönetimi %20
- İletişim Açıklığı %15

Kamusal paylaşım ve yorumların saygı/üslup sinyalleri ilgili davranış alanlarını günceller. İnsan-kalibre Niyet–Algı Uyumu, Niyet Kayması, Algı Belirsizliği ve Algı Kararlılığı özellikle İletişim Açıklığı alanına girer. Özel sohbetlerde yalnızca kullanıcının kendi mesajından türetilen yapılandırılmış davranış sinyalleri düşük ağırlıkla skoru etkiler; karşı tarafın saldırgan davranışı kullanıcıya ceza olarak yazılmaz.

3.600 bağımsız insan algısı etiketi kişiye doğrudan puan vermek için kullanılmaz. Bu veri, okuyucu algısı sinyallerinin güvenilirliğini kalibre eden araştırma katmanıdır.

### 3. Sohbet skorları
- NİYET skorunun altında `Sohbet Sağlığı Ortalaması` gösterilir.
- `Sohbet Genel Skoru`, kullanıcının kendi sohbet davranış katkısının ortalamasıdır.
- Kullanıcı profilinde hem Sohbet Genel Skoru hem Sohbet Sağlığı Ortalaması görünür.

### 4. Sohbet güvenliği
Hem 18+ Standart Modda hem 18 yaş altı Korumalı Modda Sohbet Sağlığı `50/100` veya altına indiğinde güvenlik seçenekleri açılır.

18+:
- Engelle
- Sohbete devam et

18 yaş altı:
- Engelle
- Sohbete devam et
- Ebeveyne / güvendiğin yetişkine yönlendir

`Sohbete devam et` seçildiğinde mevcut sağlık değeri kaydedilir. Sağlık 5 puan daha düştüğünde seçenekler tekrar açılır.

### 5. Çocuk modunda Tartışma Isısı koruması
18 yaş altı modda bir paylaşımın Tartışma Isısı `50/100` üzerine çıktığında:
- uyarı gösterilir,
- çocuk o paylaşımda yeni yorum gönderemez,
- paylaşımı okumaya devam edebilir.

18+ modda kullanıcının kendi yorumu Isıyı `80/100` veya üzerine çıkarırsa mevcut yorum kilidi korunur.

### 6. Sabit başlangıç Tartışma Isısı
Bütün yorum zincirleri `10/100` başlangıç değerinden başlar. Başlangıç ısısı rastgele veya gönderiye göre atanmaz. Sonraki değerler yorum olaylarıyla dinamik güncellenir.

### 7. Gönderim ve arayüz temizliği
- Sohbet mesajı Enter ile gönderilebilir.
- Yorum/yanıt kutularında Enter, Gönder düğmesiyle aynı işlemi yapar.
- `Yanıt yaz...` alanındaki gereksiz “kendi paylaşımına da yorum yapabilirsin” metni kaldırılmıştır.
- Üst çubuktaki gereksiz `Ara` kutusu kaldırılmıştır.

## Algı motoru

Akış:

`Mesaj → kör okuyucu algısı → insan kalibrasyonu → Niyet–Algı / Niyet Kayması / Belirsizlik → Algı Kararlılığı → tavsiye amaçlı Minimum Müdahale`

Algı Kararlılığı ve Minimum Müdahale yüzdeleri API bağlıyken gerçek ikinci çıkarımlar üzerinden hesaplanır. API bağlı değilse sistem bu değerlere sahte yüzdeler üretmez.

## Araştırma altyapısı
- 450 Türkçe sosyal medya mesajı
- 8 bağımsız okuyucu / mesaj
- 3.600 bağımsız insan algısı etiketi
- 7 algı sınıfı
- 5-fold out-of-fold kalibrasyon doğrulaması
- Ridge çok çıktılı kalibrasyon + simplex projection

## Dosyalar
- `index.html` — V13.2 arayüz ve istemci davranış motoru
- `run_v13.py` — Python backend ve API katmanı
- `calibration_profile.json` — insan algısı kalibrasyon profili
- `research_evidence/` — araştırma/doğrulama çıktıları
- `videos/` — mikro öğrenme içerikleri
- `V13_2_DEGISIKLIK_NOTLARI.md` — sürüm farkları
- `V13_2_TEST_NOTLARI.md` — yapılan regresyon kontrolleri
