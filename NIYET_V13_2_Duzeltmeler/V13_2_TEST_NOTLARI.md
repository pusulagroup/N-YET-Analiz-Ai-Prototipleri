# NİYET V13.2 Regresyon Test Notları

Bu dosya paketleme öncesinde yapılan yerel kontrolleri özetler.

## Statik / sözdizimi
- `run_v13.py` Python derleme kontrolünden geçirildi.
- `index.html` içindeki JavaScript Node sözdizimi kontrolünden geçirildi.
- Üst çubukta arama input'u bulunmadığı doğrulandı.
- Görünür Minimum Müdahale alanında otomatik `Değişikliği uygula` / `Uygula` butonu bulunmadığı doğrulandı.
- Yanıt alanlarının `Yanıt yaz...` olduğu ve Enter handler taşıdığı doğrulandı.
- `INITIAL_THREAD_HEAT = 10` olduğu ve gömülü başlangıç `heatBase` değerlerinin 10 olduğu doğrulandı.

## Güvenlik kuralları
- 18+ ve 18 yaş altı için güvenlik eşiği 50/100.
- Eşik altında karşı taraf risk etiketi olmasa dahi eylem paneli görünür.
- Yetişkinde ebeveyne/yetişkine yönlendirme butonu yoktur.
- Çocuk modunda yönlendirme butonu vardır.
- “Sohbete devam et” seçimi `reopenAt = mevcut sağlık - 5` olarak kaydedilir.
- Sağlık yeniden açılma noktasına ulaştığında dismissal kaydı temizlenir.
- Çocuk modunda Tartışma Isısı >50 olduğunda yorum kutusu kilitlenir.

## Skor politikası
- Genel NİYET alan ağırlıkları 25/20/20/20/15 olarak korunur.
- Niyet Kayması, Algı Kararlılığı ve insan-kalibre algı sinyalleri İletişim Açıklığı hedefinde kullanılır.
- 3.600 insan etiketi kullanıcıya doğrudan puan vermez.
- Karşı tarafın özel sohbet davranışı kullanıcının NİYET alanlarına doğrudan ceza yazmaz.

## Sunucu
- Varsayılan port: 8847
- `/api/status` sürüm: 13.2
- OpenAI anahtarı bulunmadığında status `configured: false` döndürür; anahtar ifşa edilmez.
- Sentetik güvenlik test botları API anahtarı olmadan yerel test motoruyla çalışabilir.

## Gerçek yerel çalıştırma kontrolü
- Python sunucusu 8847 portunda başlatıldı.
- `/` ana sayfası başarıyla döndü ve V13.2 başlığı doğrulandı.
- `/api/status` yanıtında `version: 13.2`, `configured: false` ve 3.600 etiketli insan kalibrasyonu metadatası doğrulandı.
- `tolga` sentetik güvenlik test botu `/api/chat` üzerinden API anahtarı olmadan yanıt üretti.
