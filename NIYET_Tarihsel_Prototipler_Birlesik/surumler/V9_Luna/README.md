# NİYET V9 — GPT-5.6 Luna

V9, V8.1 üzerine sosyal iletişim araştırma katmanlarını ekler ve özellikle **“NİYET ile kontrol et”** akışını yeniden kurar.

## V9 yenilikleri
- **NİYET ile kontrol et düzeltildi:** API bağlı değilken bile yerel ön analiz çalışır; API bağlıysa GPT-5.6 Luna + NİYET karar katmanı devreye girer.
- **İnsan Algısı Kalibrasyon Katmanı:** LLM ham dağılımı doğrudan son karar değildir. `calibration_profile.json` üzerinden modelden bağımsız kalibrasyon uygulanır. Anket sonuçları henüz eklenmediği için dosya `survey_pending` durumundadır.
- **Algı Belirsizliği:** Okuyucu niyet dağılımının normalize entropisi 0–100 aralığında hesaplanır. Belirsizlik yüksekse sistem kesin Niyet Kayması hükmü vermez.
- **Algı Sapma Haritası:** Mizah→Alay, Eleştiri→Kişisel saldırı, Tavsiye→Üstten/Kovucu konuşma gibi nitel sapmalar gösterilir.
- **Karşı-Olgusal Algı Simülatörü:** Luna tek analiz çağrısında 3 minimal ifade alternatifi ve beklenen niyet dağılımlarını üretir. API yoksa yerel minimal alternatifler gösterilir.
- **Tartışma Isısı + İvme + Yön:** Her yorum zincirinde yalnızca mevcut ısı değil, son değişim, ivme ve “yükseliyor / sakinleşiyor” yönü gösterilir.
- **Bağlamsal İletişim Profili:** Genel iletişim, provokasyon altında, karşı görüşte ve mizah kullanırken davranış ayrı takip edilir; tek bir sosyal kredi mantığına indirgenmez.
- **Davranış Doğrulamalı Müdahale Öğrenmesi:** Mikro eğitimden sonra gerçek etkileşimlerde hedef davranış görülme oranı takip edilir.
- **Gizlilik Eşikli Özel Sohbet:** Özel mesajlar genel skora doğrudan yazılmaz. Sohbet Sağlığı 30 altına kullanıcı kaynaklı ciddi düşerse ham metin değil yapılandırılmış ihlal özeti genel profile kontrollü etki eder.
- **Sosyal farkındalıklı bot politikası:** Sohbet ve yorum botları yüksek algı belirsizliğinde niyeti kesin varsaymama, yüksek gerilimde tartışmayı büyütmeme ilkesiyle yanıt verir.
- **Tek çağrıda sohbet turu:** `/api/chat` ve `/api/bot_comment` yanıt + kullanıcı analizi + bot yanıt analizi için tek yapılandırılmış model çağrısı kullanır.

## Başlatma

### Windows
`V9_BASLAT_WINDOWS.bat`

### Mac / Linux
`V9_BASLAT_MAC_LINUX.command`

Tarayıcı adresi: `http://127.0.0.1:8819/`

V9, eski V8.1 sunucusuyla karışmaması için **8819** portunu kullanır. Üst çubukta **V9 · Luna** görmelisiniz.

## API
İlk açılışta API anahtarı zorunlu değildir. Paylaşım öncesi NİYET kontrolü yerel ön analizle çalışır. GPT-5.6 Luna kullanmak için üstteki “OpenAI bağlanmadı” durumuna tıklayıp API anahtarını girin.

## Anket sonrası kalibrasyon
Şu anda `calibration_profile.json` insan verisi bekleme modundadır. 450 mesaj × 8 okuyucu = 3.600 algı etiketi toplandıktan sonra bu dosyanın sıcaklık, sınıf önyargıları ve karar eşikleri veriyle güncellenebilir. Böylece aynı NİYET kalibrasyon katmanı Luna veya başka bir LLM üzerinde kullanılabilir.
