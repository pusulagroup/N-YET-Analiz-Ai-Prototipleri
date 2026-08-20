# NİYET — VFINAL2

VFINAL2, yarışma öncesi ürün dondurma ve stabilizasyon sürümüdür. **VFINAL2 adı kullanıcı arayüzünde gösterilmez**; üst çubukta yalnızca N’SOSYAL × NİYET markası görünür.

## Öne çıkan durum
- NİYET Skoru: Saygı, Yapıcılık, Tutarlılık, Gerilim Yönetimi ve İletişim Açıklığı alanlarının eşit ağırlıklı (%20) aritmetik ortalaması.
- Beğeni ve yeniden paylaşım sosyal etkileşimdir; NİYET/Saygı skorunu artırmaz.
- Açık hakaret/aşağılayıcı dil, dış AI yanıtı beklenmeden hızlı güvenlik uyarısına alınır; “nefret söylemi” ile karıştırılmaz.
- AI servis gecikmesi veya kesintisinde yerel ön analiz ve anlaşılır tekrar-dene/fallback davranışı korunur.
- Sohbet; metin, Sohbet Sağlığı, favori/arşiv/engel, okunmamış sayaçları ve test botlarıyla çalışır.
- **Sohbete fotoğraf/görsel veya dosya yükleme özelliği kaldırılmıştır.** Multimodal görsel yorumlama uç noktası da kaldırılmıştır.
- Akıştaki mevcut demo görselleri, avatarlar ve 25 mikro eğitim videosu korunur.
- SEO (`robots.txt`, `sitemap.xml`), mobil uyumluluk ve Render dağıtım yapısı korunur.

## Yerel çalıştırma
Windows: `BASLAT_VFINAL2_WINDOWS.bat`

macOS/Linux: `BASLAT_VFINAL2_MAC_LINUX.command`

Tarayıcı otomatik olarak `http://127.0.0.1:10000` adresini açar. AI özellikleri için `OPENAI_API_KEY` yalnızca yerel `.env.local` veya sunucu ortam değişkeninde tutulmalıdır.

## Render
Build Command: `pip install -r requirements.txt`

Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 240 app_v16_2:app`

Render giriş noktası bilerek `app_v16_2:app` olarak korunmuştur; bu, çalışan dağıtım yapılandırmasını değiştirmemek içindir.
