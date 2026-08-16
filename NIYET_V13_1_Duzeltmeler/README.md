# NİYET V13.1 — Algı Kararlılığı + Güvenli Minimum Müdahale

V13.1, V12.4'teki insan-kalibre Niyet–Algı motorunu korur ve iki yeni özelliği tek karar zincirinde birleştirir:

**Niyet–Algı Analizi → Algı Kararlılığı → Minimum Müdahale → gerçek yeniden ölçüm**

## V13.1’de ana yapı

### 1. Algı Kararlılığı
Algı Kararlılığı, bir mesajın mevcut algı dağılımının küçük ve kontrollü ifade değişikliklerinde ne kadar korunduğunu ölçer.

- İlk okuyucu algısı, yazarın seçtiği niyet gösterilmeden kör biçimde çıkarılır.
- Sistem anlamı mümkün olduğunca koruyan mikro-varyasyonlar üretir.
- Bu varyasyonlar ikinci bir kör algı çıkarımından geçirilir.
- Her dağılım aynı 3.600 insan etiketiyle öğrenilmiş kalibrasyon profilinden geçirilir.
- Orijinal ve varyasyon dağılımları arasındaki normalize Jensen–Shannon uzaklığı 0–100 Algı Kararlılığı skoruna dönüştürülür.

Bu nedenle Algı Kararlılığı, LLM'in doğrudan uydurduğu bir puan değildir.

### 2. Minimum Müdahale
Minimum Müdahale, kullanıcının seçtiği niyete daha yüksek algı uyumu sağlayabilecek küçük değişiklikleri arar.

- Aday üretiminde yazarın beyan ettiği niyet kullanılabilir; bu işlem ham algı tahmininden sonradır.
- Aday metinlerin başarı yüzdeleri aday üreticisi tarafından tahmin edilmez.
- Her aday ayrıca kör ikinci algı çıkarımı + insan kalibrasyonundan geçirilir.
- Uyum kazancı, yanlış anlaşılma riski ve değişiklik maliyeti gerçek yeniden ölçümden hesaplanır.
- Sistem, algı kazancını değişiklik maliyetine göre değerlendirerek kullanıcının üslubunu mümkün olduğunca korumayı hedefler.

API bağlı değilse bu iki özellik için sahte yüzde üretilmez; arayüz açıkça gerçek ikinci çıkarım gerektiğini belirtir.

### 3. V13.1 algı güvenlik filtresi
V13.1, Minimum Müdahale adaylarını yalnızca niyet uyumu artışına göre seçmez. Bir adayın kullanıcıya gösterilebilmesi için:

- seçilen niyetin algı payını ölçülebilir biçimde artırması,
- yanlış anlaşılma riskini düşürmesi,
- Algı Belirsizliğini anlamlı biçimde artırmaması,
- mevcut mesajda olmayan yeni bir baskın algı sapması oluşturmaması,
- değişiklik maliyetinin minimal müdahale sınırında kalması gerekir.

Tüm adaylar kötüleşiyorsa sistem kötü öneriyi seçmek yerine **“Güvenilir minimal iyileştirme bulunamadı”** sonucunu gösterir. V13.1 ayrıca Algı Belirsizliğini yalnızca entropiyle ölçmez; insan-kalibre dağılımdaki en güçlü iki algının yakınlığını merkeze alan daha seçici bir skor kullanır. Böylece doğal olarak yumuşak kalibrasyon dağılımları gereksiz yere 70+ belirsizlik üretmez.

### 4. Paylaşım öncesi NİYET Rehberi
Kullanıcı mesaj yazmadan önce seçtiği niyete göre kısa iletişim önerileri görür. Rehber; yanlış anlaşılabilecek, niyetten farklı algılanabilecek ve gereksiz gerilim oluşturabilecek ifade kalıplarından mümkün olduğunca kaçınmaya yardımcı olur. Bu aşamada analiz puanı üretilmez.

## V13/V13.1 profil / arayüz regresyon düzeltmeleri

- Gönderi avatarı, kullanıcı adı ve kullanıcı etiketi aynı profil yönlendirmesini kullanır.
- Yorum avatarı ve yorumcu adı hem kullanıcı profiline hem de kendi profile güvenilir biçimde yönlenir.
- Üst çubuktaki kullanıcı alanı doğrudan kendi profile açılır.
- Public profile → sohbet → geri akışı korunur; sohbetten geri dönüldüğünde aynı profile dönülür.
- Kapak/avatar negatif hizalama, z-index, object-fit, aspect-ratio ve overflow davranışları yeniden düzenlendi.
- Gönderi görselleri mobil/masaüstünde kontrollü 16:9 medya alanında gösterilir; taşma ve üst üste binme azaltıldı.
- Mobil profil üst alanı, sayaçlar, yorum balonları ve müdahale kartları için ek responsive kurallar eklendi.

## Tartışma Isısı

V12.4 dinamik ısı mantığı korunmuştur:

- Her yorum `heatBefore`, `heatAfter`, `heatDelta` bilgisi taşır.
- Sert / saldırgan / kovucu yorumlar ısıyı düşüremez.
- Sakinleştirici ve yapıcı yorumlar kontrollü soğuma oluşturabilir.
- Yorum kutuları ısı yükseldikçe açık maviden açık kırmızı/bordo tonlarına geçer.
- Her yorumda geçiş sırası açık biçimde örneğin `Isı 42 → 56 · +14` olarak gösterilir.
- Kullanıcının kendi yorumu Tartışma Isısını **80/100 veya üzerine çıkarırsa** o paylaşım için yeni yorum gönderme kilitlenir ve kullanıcıya uyarı gösterilir.

## İnsan algısı kalibrasyonu

- 450 Türkçe sosyal medya mesajı
- mesaj başına 8 bağımsız okuyucu
- toplam 3.600 bağımsız insan algısı etiketi
- 7 algı sınıfı
- multi-output Ridge regression + simplex projection
- 5-fold stratified cross-validation
- yazarın seçtiği niyet kalibrasyon modelinin girdisi veya hedefi değildir

Araştırma benchmarkı:

- Ham Luna baskın algı doğruluğu: yaklaşık **%64,8**
- Kalibre NİYET baskın algı doğruluğu: yaklaşık **%76,4**
- Kalibre Top-2: yaklaşık **%92,4**

## Yaş ve dijital güvenlik yaklaşımı

Girişte yalnızca iki yaş seçeneği bulunur:

- **18 yaşından küçüğüm**
- **18 yaşındayım veya daha büyüğüm**

18 yaş altı kullanıcılar aynı uygulamayı kullanır; yalnızca koruyucu güvenlik müdahaleleri daha görünür ve hassas çalışır. Yaşa göre profil gizleme veya iletişim puanı eşiği uygulanmaz.

V13.1 güvenlik eşikleri:
- 18 yaş altı modda **Sohbet Sağlığı 50/100 ve altına** indiğinde `Engelle`, `Sohbete devam et` ve `Ebeveyne / güvendiğin yetişkine yönlendir` seçenekleri açılır.
- Standart modda aynı müdahale seçenekleri **30/100 ve altına** indiğinde açılır; yetişkine yönlendirme seçeneği gösterilmez.
- Tekrarlayan zararlı davranışlarda Sohbet Sağlığı düşüşü hızlandırılmıştır; olumlu toparlanma ise kademeli kalır.

## Başlatma

### Windows
`V13_1_BASLAT_WINDOWS.bat`

### Mac / Linux
`V13_1_BASLAT_MAC_LINUX.command`

Varsayılan adres:
`http://127.0.0.1:8846/`

## API güvenliği

OpenAI çağrıları Python backend üzerinden yapılır. `OPENAI_API_KEY` ortam değişkeninden okunabilir veya prototip oturumunda backend'e gönderilebilir; anahtar kaynak kodun içine yazılmamalı ve repoya commit edilmemelidir.

## Ana dosyalar

- `index.html` — V13.1 kullanıcı arayüzü
- `run_v13.py` — yerel sunucu, kör algı çıkarımı, insan kalibrasyonu, Algı Kararlılığı ve Minimum Müdahale motoru
- `calibration_profile.json` — 3.600 insan etiketiyle öğrenilen deployment kalibrasyon profili
- `lesson_manifest.json` + `videos/` — mikro öğrenme içerikleri
- `research_evidence/` — araştırma ve doğrulama kanıtları
