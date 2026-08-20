# CHANGELOG — VFINAL2

- Üst arayüzde sürüm rozeti tamamen kaldırıldı; VFINAL2 yalnızca paket/teknik sürüm adıdır.
- Sohbetteki `+` ek menüsü, görsel/fotoğraf seçimi, dosya ekleme önizlemesi ve multimodal görsel yorumlama kaldırıldı.
- `/api/chat_media` uç noktası hem Flask katmanından hem yerel yedek sunucudan kaldırıldı.
- Sohbet yeniden metin tabanlıdır; Sohbet Sağlığı, okunmamış sayaçları, favori/arşiv/engel ve sert-konuşma test botları korunmuştur.
- AI ana analiz istemci timeout değeri 35 saniyeden 20 saniyeye indirildi; gecikmede mevcut yerel ön analiz/fallback akışı korunur.
- Açık hakaret/aşağılayıcı dil hızlı uyarısı korunmuştur ve nefret söylemi olarak yanlış etiketlenmez.
- Beğeni/yeniden paylaşımın Saygı veya genel NİYET Skoruna etkisi yoktur.
- Genel NİYET Skoru 5 alan × %20 aritmetik ortalamadır.
- Profil repost akışı, Tartışma Isısı örnekleri, SEO, domain, mobil düzen ve 25 eğitim videosu korunmuştur.
