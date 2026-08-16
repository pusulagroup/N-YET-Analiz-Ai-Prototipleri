# NİYET V13.5 — Algı Kararlılığı ve Öneri Stabilizasyonu

V13.5, V13.3 hattındaki iki ana problemi hedefler: Minimum Müdahale önerilerinin gereksiz biçimde kaybolması ve Sohbet Genel Skorunun kullanıcıya görünen sohbet sağlıklarının aritmetik ortalamasıyla uyuşmaması.

## Başlatma
- Windows: `V13_4_BASLAT_WINDOWS.bat`
- macOS / Linux: `V13_4_BASLAT_MAC_LINUX.command`
- Varsayılan adres: `http://127.0.0.1:8850/`

## V13.5 odak noktaları
- Algı Kararlılığı yalnızca serbest yeniden yazımlara dayanmaz; emoji, vurgu ve noktalama gibi kontrollü yüzey mikro-varyasyonları da kullanılır.
- Kararlılık, mikro-varyasyonların kör ikinci algı çıkarımı ve insan kalibrasyonu sonrası Jensen–Shannon uzaklıklarından hesaplanır.
- Minimum Müdahale aday havuzu genişletildi ve üç kademeli güvenlik kapısı kullanılıyor: doğrulanmış minimal, yüksek kazançlı ve isteğe bağlı minimal.
- Güvenilir en az bir minimal seçenek varsa, mesaj kararlı olsa bile öneri alanı tamamen kaybolmaz.
- Öneriler ayrı kör çıkarım + insan kalibrasyonu ile ölçülmeden yüzde/Algı Kazancı göstermez.
- `Değişikliği uygula` yeniden analiz döngüsü başlatmadan, daha önce doğrulanmış öneriyi doğrudan paylaşır.
- Sohbet Genel Skoru aktif ve engellenmemiş sohbetlerin Sohbet Sağlığı değerlerinin doğrudan aritmetik ortalamasıdır.
- Engellenen sohbetler genel ortalamaya dahil edilmez.

## Araştırma altyapısı
Kalibrasyon katmanı 450 Türkçe mesaj üzerindeki 3.600 bağımsız insan algısı etiketini kullanır. Yazarın seçtiği niyet kör okuyucu algısı çıkarımına veya kalibrasyon modelinin eğitim hedefine verilmez.


## V13.5 API bağlantı düzeltmesi
- API anahtarı artık `/v1/models` ile değil, NİYET'in gerçekten kullandığı `/v1/responses` üzerinden doğrulanır.
- Böylece Models endpoint izni kapalı olan kısıtlı proje anahtarlarında oluşabilecek yanlış bağlantı hatası önlenir.
- Anahtar + seçili model + kota/erişim aynı küçük bağlantı isteğinde birlikte test edilir.
- Hata durumunda 401/403/404/429 ve ağ bağlantısı için daha açıklayıcı mesaj gösterilir.
- API anahtarı yine yalnızca Python sürecinin belleğinde tutulur; dosyaya yazılmaz.
