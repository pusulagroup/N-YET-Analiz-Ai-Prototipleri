# NİYET V14.1

NİYET, kullanıcının söylemek istediği ile okuyucunun algılayabileceği arasındaki farkı insan algısı verisiyle kalibre ederek görünür kılan açıklanabilir sosyal yapay zekâ prototipidir.

## Başlatma

### Windows
`V14_1_BASLAT_WINDOWS.bat`

### macOS / Linux
`V14_1_BASLAT_MAC_LINUX.command`

Varsayılan port `8853`'dir. Port doluysa Python sunucusu sonraki dört portu sırayla dener.

## OpenAI bağlantısı
Uygulama içindeki bağlantı ekranından API anahtarı girilir. Anahtar HTML içine veya dosyaya yazılmaz; yalnızca çalışan Python sürecinin belleğinde tutulur. `.env` veya anahtar içeren başka dosyaları repoya eklemeyin.

## V14 ana akışı

- **Paylaşım:** hızlı NİYET analizi → arka planda Algı Kararlılığı + Minimum Müdahale.
- **Yorum:** Tartışma Isısı → arka planda kısa Algı Belirsizliği uyarısı + Gölge Niyet.
- **Sohbet:** Sohbet Sağlığı → yaşa duyarlı güvenlik → arka planda Gölge Niyet.
- **Genç Mod:** paylaşım, yorum ve sohbette daha erken koruyucu mikro uyarılar; koyu gri / beyaz görsel tema.

## Veri ve kalibrasyon
- 450 Türkçe sosyal medya mesajı.
- Her mesaj için 8 bağımsız okuyucu.
- Toplam 3.600 bağımsız insan algısı etiketi.
- Ham okuyucu algısı yazarın seçtiği niyeti görmez.
- İnsan-kalibre dağılım Ridge çoklu çıktı + simplex projection katmanından gelir.

Araştırma dosyaları `research_evidence/` altında tutulur. Kişisel katılımcı verileri repoya eklenmemelidir.


## V14.1 düzeltmeleri
- Nötr/kibar bir yorum artık tek başına Tartışma Isısını düşürmez; düşüş için açık gerilim azaltma sinyali gerekir.
- Gölge Niyet'e bağlam ilgisi kapısı eklendi; konu dışı/rastgele yorumlar bağlam nedeniyle Orta/Yüksek sayılmaz.
- Sohbet Genel Skoru tüm normal botları başlangıçta 100 kabul ederek hesaplanır. Örn. 20 botta tek sohbet 33 ise skor `(19×100+33)/20 ≈ 97` olur.
- Engellenen hesaplar Sohbet Genel Skoru paydasından çıkarılır; güvenlik-test botları genel profile dahil edilmez.
