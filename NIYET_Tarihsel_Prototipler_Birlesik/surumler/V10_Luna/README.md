# NİYET V10 — Luna + Dijital Güvenlik

V10, V9 arayüzünü koruyarak siber zorbalık / çevrimiçi taciz erken uyarısı, yaşa duyarlı kullanım modları ve Genel Sohbet Skoru ekler.

## V10 yenilikleri

- **Yaş aralığı kapısı**
  - **14 yaş ve altı:** Eğitim Modu. Yalnızca 25 mikro öğrenme videosu ve quizler açıktır; akış, profil, sohbet ve NİYET skoru kapalıdır.
  - **15–17 yaş:** Genç Mod. NİYET skoru 70 altındaki sentetik profiller görünmez. Mesajlaşma için karşı profilin Genel Sohbet Skoru ayrıca **70'in üzerinde** olmalıdır.
  - **18+:** Standart Mod. Sosyal prototipin tamamı açıktır; dijital güvenlik uyarıları yine çalışır.
  - Üstteki yaş modu rozeti tıklanarak demo sırasında mod değiştirilebilir.

- **Genel Sohbet Skoru**
  - Kullanıcının iletişime girdiği özel sohbetlerde **kendi davranış katkısının sohbet bazlı ortalaması**dır.
  - Karşı tarafın zorbalığı / tacizi mağdur olan kullanıcının Genel Sohbet Skorunu düşürmez.
  - Her sohbetin kendi **Sohbet Sağlığı** ayrı tutulmaya devam eder.

- **Karşı tarafa açıklanan risk nedenleri**
  - Sohbet Sağlığını düşüren kişisel saldırı, kovucu/baskıcı dil, küçümseme ve gerilim sinyalleri davranışı yapan kişiye değil, maruz kalan karşı tarafa gösterilir.
  - Özel mesajların ham içeriği genel profile taşınmaz.

- **Dijital Güvenlik Sinyalleri**
  - Kişisel saldırı / hakaret
  - Kovucu veya baskıcı dil
  - Küçümseyici dil
  - Gerilim artırma
  - Açık sınır ihlali
  - Tekrarlı istenmeyen temas
  - Açık tehdit / korkutma sinyali
  - İstenmeyen cinselleştirilmiş yaklaşım sinyali
  - Son dört sinyal bağlam gerektirir ve tek belirsiz cümleden çıkarılmaz.

- **Dijital Güvenlik Uyarısı**
  - Karşı tarafın davranış katkısı kötüleştiğinde sohbet içinde yapılandırılmış uyarı açılır.
  - Genç Modda: **Yanıt vermeden çık, Sessize al, Güvendiğin yetişkinle paylaş, Engelle** seçenekleri gösterilir.
  - Paylaşılabilir özet ham mesajları değil yapılandırılmış risk sinyallerini içerir.

- **İki güvenlik test botu**
  - **Tolga Sert — TEST:** NİYET 74, Genel Sohbet 76. Genç Mod filtresini geçer; sohbet sırasında kontrollü tersleyici davranış üreterek erken uyarının sonradan devreye girmesini test eder.
  - **Berk Koral — TEST:** NİYET 58, Genel Sohbet 54. Yetişkin modunda görünür; Genç Modda hem görünürlük hem iletişim filtresi tarafından dışarıda bırakılır.
  - Bu test botları **OpenAI API anahtarı olmadan da** deterministik şekilde çalışır. Gerçek tehdit, nefret söylemi, cinsel taciz veya fiziksel zarar içeriği üretmezler.

- **Genç Mod filtre mantığı**
  - Görünürlük: `NİYET Skoru >= 70`
  - Mesajlaşma: `NİYET Skoru >= 70` **ve** `Genel Sohbet Skoru > 70`
  - Diğer kullanıcıların NİYET puanı arayüzde yayınlanmaz; eşik yalnızca güvenlik filtresinde kullanılır.

- **V9 katmanlarının tamamı korunur**
  - NİYET ile kontrol et
  - İnsan algısı kalibrasyon altyapısı
  - Algı belirsizliği / belirsizlikte karar vermeme
  - Algı Sapma Haritası
  - Karşı-Olgusal Algı Simülatörü
  - Tartışma Isısı + İvme + Yön
  - Bağlamsal İletişim Profili
  - Davranış Doğrulamalı Mikro Öğrenme
  - Gizlilik Eşikli Özel Sohbet

## Başlatma

### Windows
`V10_BASLAT_WINDOWS.bat`

### Mac / Linux
`V10_BASLAT_MAC_LINUX.command`

Adres: `http://127.0.0.1:8820/`

Üst çubukta **V10 · Luna** görünmelidir.

## Hızlı güvenlik testi

1. Uygulamayı açın ve **15–17 · Genç Mod** seçin.
2. Sohbet sekmesine girin.
3. Listenin üst kısmındaki **Tolga Sert · TEST** profilini açın.
4. Bir veya iki normal yanıt verin.
5. Kontrollü tersleyici cevaplar geldikçe karşı taraf davranış katkısı düşer ve **Genç Mod · Dijital Güvenlik Uyarısı** görünür.
6. Mod rozetinden **18+** seçildiğinde **Berk Koral · TEST** de görülebilir.

## Tasarım notu

Genel Sohbet Skorunda tüm sohbet sağlığının kaba ortalamasını kullanmak, zorbalığa maruz kalan kişiyi de cezalandırabilirdi. Bu nedenle V10'da Genel Sohbet Skoru kullanıcının **kendi mesajlarının o sohbetlerde oluşturduğu davranış katkısının ortalaması** olarak uygulanmıştır. Sohbet Sağlığı ise ilişkinin bütününe ait ayrı bir göstergedir.
