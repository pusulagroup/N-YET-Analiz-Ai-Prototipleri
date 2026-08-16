# NİYET V13.6 — Sade Analiz ve Sohbet Stabilizasyonu

V13.6, V13.5'in Algı Kararlılığı ve Minimum Müdahale yapısını korurken iki kullanıcı deneyimi sorununa odaklanır: paylaşım analizindeki teknik ayrıntı kalabalığı ve özel sohbet botlarının ağır yapılandırılmış API çağrısı nedeniyle kırılganlaşması.

## Başlatma
- Windows: `V13_6_BASLAT_WINDOWS.bat`
- macOS / Linux: `V13_6_BASLAT_MAC_LINUX.command`
- Varsayılan adres: `http://127.0.0.1:8851/`

## V13.6 değişiklikleri
- Paylaşım analizindeki **Analiz detayları** bölümü **Ek analiz** olarak sadeleştirildi.
- Ham model dağılımı, ayrı kalibrasyon dağılımı ve uzun yöntem açıklamaları normal kullanıcı ekranından çıkarıldı.
- Ek analizde yalnızca Algı Belirsizliği, Tartışma Tetikleme, Niyet Kayması ve diğer en güçlü üç olası okuyucu algısı gösterilir.
- Normal `/api/analyze` yanıtından arayüzün kullanmadığı ham dağılım ve stability-variant araştırma çıktıları çıkarılır.
- Özel sohbet botlarında model artık tek çağrıda yalnızca doğal konuşma yanıtını üretir; büyük `reply + user_analysis + reply_analysis` JSON şeması kullanılmaz.
- Sohbet Sağlığı ve skor için gerekli hızlı davranış sinyalleri ayrı yerel katmanda çıkarılır. Bu katman özel mesaj metnini profile taşımaz.
- Geçici sohbet API hatasında sohbet kilitlenmek yerine `V13.6 yerel sohbet yedeği` etiketiyle sınırlı bir yedek yanıt kullanır.

## Korunan V13 özellikleri
- Algı Kararlılığı kontrollü mikro-varyasyonların kör ikinci çıkarımı ve insan kalibrasyonuyla hesaplanır.
- Minimum Müdahale adayları ayrı kör çıkarım + insan kalibrasyonu ile doğrulanmadan Algı Kazancı göstermez.
- `Değişikliği uygula`, daha önce doğrulanmış öneriyi yeniden analiz döngüsüne sokmadan paylaşır.
- Sohbet Genel Skoru aktif ve engellenmemiş sohbetlerin Sohbet Sağlığı değerlerinin aritmetik ortalamasıdır.
- Yaşa duyarlı sohbet ve Tartışma Isısı güvenlik eşikleri korunur.

## Araştırma altyapısı
Kalibrasyon katmanı 450 Türkçe mesaj üzerindeki 3.600 bağımsız insan algısı etiketini kullanır. Yazarın seçtiği niyet kör okuyucu algısı çıkarımına veya kalibrasyon modelinin eğitim hedefine verilmez.

## API
- API anahtarı NİYET'in kullandığı `/v1/responses` üzerinden doğrulanır.
- Anahtar yalnızca çalışan Python sürecinin belleğinde tutulur; dosyaya veya tarayıcı koduna yazılmaz.
