# NİYET V11 — Anket Entegre / İnsan Kalibrasyonlu Luna

V11, V10'daki sosyal ağ, Genç Mod, Sohbet Sağlığı, Tartışma Isısı/İvmesi, mikro öğrenme ve dijital güvenlik katmanlarını korur; ancak paylaşım öncesi Niyet–Algı motorunu artık **tamamlanan insan araştırmasına göre kalibre eder**.

## V11'de gerçekten ne değişti?

Ana akış artık şöyledir:

**GPT-5.6 Luna → ham 7-sınıflı okuyucu algısı → NİYET insan-algısı kalibrasyonu → kalibre okuyucu dağılımı → Niyet Kayması / Algı Belirsizliği / Yanlış Anlaşılma Riski**

Kalibrasyon profili:

- 450 Türkçe sosyal medya mesajı
- mesaj başına 8 bağımsız okuyucu
- toplam 3.600 bağımsız insan algısı etiketi
- hedef: 7-sınıflı insan **soft-label** algı dağılımı
- yazarın seçtiği niyet eğitim hedefi değildir
- canlı paylaşım analizinde de yazarın seçtiği niyet Luna’nın ham algı tahminine gösterilmez; kör benchmark mantığı korunur
- algoritma: multi-output Ridge regression + olasılık simplex projeksiyonu
- doğrulama: 5-fold stratified cross-validation

Araştırma benchmarkı:

- Ham Luna baskın algı doğruluğu: **%64,8**
- Kalibre NİYET baskın algı doğruluğu: **%76,4**
- Kalibre Top-2: **%92,4**
- Bir okuyucu ↔ diğer 7 okuyucunun baskın algısı referansı: **%71,0**
- Sıkı temizlenmiş sette baskın Niyet Kayması: **yaklaşık %27,1**

## Paylaşım öncesi analiz ekranı

V11 analiz modali artık iki dağılımı yan yana/ardışık gösterir:

1. **Ham Luna okuyucu algısı**
2. **NİYET insan-kalibre okuyucu algısı**

Böylece jüri, insan verisinin model çıktısını gerçekten nasıl değiştirdiğini tek örnek üzerinde görebilir.

> Not: API bağlantısı yoksa arayüz çalışmaya devam eder ve yerel ön analiz gösterir. Bu yerel ön analiz, gerçek Luna çıktısı olmadığı için "nihai insan-kalibre sonuç" olarak etiketlenmez.

## Karar katmanı

- Yazar niyeti yalnızca kullanıcının beyanıdır.
- Okuyucu algısı ayrı dağılım olarak tahmin edilir.
- Yüksek algı belirsizliğinde sistem kesin Niyet Kayması hükmü vermemeye çalışır.
- Güçlü Niyet Kayması için araştırmada nested-CV ile seçilen yaklaşık **%35,5** kalibre baskın-olasılık eşiği profil içinde tutulur.

## Veri kalitesi politikası

Manuel incelemede 47 aday mesaj ayrıldı:

- 3 Güvenilir
- 25 Şüpheli
- 19 Belirsiz / bağlam yetersiz

Bu kalite taraması **algı kalibrasyon eğitimini yazar niyeti üzerinden değiştirmez**; çünkü algı modeli doğrudan 8 okuyucunun dağılımını öğrenir. Yazar etiketi yalnızca Niyet Kayması araştırma raporlamasında ayrıca kalite süzgecinden geçirilir.

## Emoji–mizah yan bulgusu

Emoji var/yok ayrımı tek başına mizahın doğru anlaşılmasını anlamlı biçimde artırmadı. Açık mizah emojilerinde ham Luna'nın insanlara göre daha yüksek mizah güveni gösterebildiği görüldü; kalibrasyon katmanı bu aşırı güveni azaltma yönünde davranabildi. Bu bulgu ana karar motoruna ayrı bir kural olarak zorla eklenmedi; araştırma kanıtı olarak saklandı.

## Başlatma

### Windows
`V11_BASLAT_WINDOWS.bat`

### Mac / Linux
`V11_BASLAT_MAC_LINUX.command`

Varsayılan adres:
`http://127.0.0.1:8830/`

Üst çubukta **V11 · İnsan Kalibrasyonlu Luna** görünmelidir.

## OpenAI bağlantısı

Arayüzde API bağlantısı yapılabilir veya terminalde `OPENAI_API_KEY` ortam değişkeni kullanılabilir. Varsayılan model `gpt-5.6-luna` olarak ayarlanmıştır.

## Korunan V10 özellikleri

- Yaş kapısı: 14 ve altı Eğitim Modu / 15–17 Genç Mod / 18+ Standart
- Genç Mod görünürlük ve mesajlaşma eşikleri
- Tolga Sert ve Berk Koral güvenlik-test botları
- Sohbet Sağlığı + Genel Sohbet Skoru
- siber zorbalık / rahatsız edici örüntü erken uyarısı
- Tartışma Isısı + İvme
- Bağlamsal İletişim Profili
- Davranış Doğrulamalı Mikro Öğrenme
- 25 mikro eğitim videosu
- karşı-olgusal algı simülatörü
- gizlilik eşikli özel sohbet

## Dosyalar

- `index.html` — V11 arayüzü
- `run_v11.py` — yerel sunucu, OpenAI çağrısı ve gerçek kalibrasyon motoru
- `calibration_profile.json` — 3.600 insan etiketiyle öğrenilen V1 deployment profili
- `lesson_manifest.json` + `videos/` — mikro öğrenme içerikleri
- `ANKET_ENTEGRASYON_NOTU.md` — araştırma verisinin ürün motoruna nasıl bağlandığının kısa teknik özeti
