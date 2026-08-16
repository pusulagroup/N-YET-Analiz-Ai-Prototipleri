# NİYET V13.1 Regresyon Test Notları

## Yapılan kontroller
- `run_v13.py` Python sözdizimi kontrolünden geçti (`py_compile`).
- `index.html` içindeki JavaScript çıkarılarak Node.js sözdizimi kontrolünden geçti (`node --check`).
- Yerel sunucu 8846 portunda başlatıldı ve `/api/status` yanıtı `version: 13.1`, `human_calibrated`, `3600` insan etiketi bilgileriyle doğrulandı.
- API anahtarı olmadan çalışan güvenlik-test botu endpoint'i kontrol edildi.

## Algı Belirsizliği regresyonu
V13'te yalnızca normalize entropi kullanıldığı için doğal olarak yumuşak insan-kalibre dağılımlar gereğinden yüksek belirsizlik üretebiliyordu. V13.1'de en güçlü iki algının yakınlığı ana sinyal olarak kullanılmaktadır.

Sentetik dağılım kontrolleri:
- Belirgin baskın algıya sahip fakat entropisi yüksek örnek: eski entropi yaklaşık `73,8/100`, yeni Algı Belirsizliği `38,4/100`.
- En güçlü iki algının neredeyse eşit olduğu örnek: yeni Algı Belirsizliği `80,8/100`.

Bu test yalnızca skor fonksiyonunun davranış regresyonudur; canlı OpenAI çıkarımı değildir.

## Minimum Müdahale güvenlik filtresi
Sentetik aday testinde 5 öneriden 3'ü; olumsuz algı kazancı, belirsizlik artışı veya minimal müdahale koşullarını karşılamadığı için reddedildi. Yalnızca 2 güvenli aday kullanıcıya gösterilebilir durumda kaldı.

V13.1 kuralı: bütün adaylar kötüleşiyorsa sistem kötü bir öneriyi göstermek yerine `Güvenilir minimal iyileştirme bulunamadı` sonucunu verir.

## Tartışma Isısı
- Isı etiketi artık kayıtlı `heatDelta` değerine güvenmek yerine `heatAfter - heatBefore` üzerinden yeniden hesaplanır.
- `heatBefore=10`, `heatAfter=47` regresyon örneğinin gösterimi: `Isı 10 → 47 · +37`.
- Kullanıcının kendi yorumu sonrasında ısı `80/100` veya üzerine çıkarsa o paylaşımda yeni kullanıcı yorumu kilitlenir.

## Sohbet Sağlığı
- Tekrarlayan zararlı davranışlarda düşüş katsayısı artırıldı ve tekrar cezası eklendi.
- Sohbet Sağlığında riskli taraf `%85`, diğer taraf `%15` ağırlıkla değerlendirilir.
- 18 yaş altı müdahale eşiği: `50/100`.
- Standart kullanıcı müdahale eşiği: `30/100`.

## Sınırlılık
Gerçek Algı Kararlılığı ve Minimum Müdahale sonuçları birden fazla canlı model çıkarımı gerektirdiği için OpenAI API anahtarı olmadan uçtan uca canlı model testi yapılmadı. Paket, API bağlandığında kötüleşen müdahale adaylarını ikinci kör çıkarım ve insan kalibrasyonundan sonra filtreleyecek şekilde hazırlanmıştır.
