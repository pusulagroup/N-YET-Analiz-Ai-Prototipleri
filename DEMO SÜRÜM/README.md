# NİYET — Final güncellemesi, 18 Eylül 2026

Sürüm: **V12-2026-09-18**. Bu klasör güncel çalışan proje kaynaklarının tam anlık görüntüsüdür. Depodaki eski prototiplerden bağımsız çalıştırılabilir. Diğer `README_V...` / değişiklik belgeleri tarihsel notlardır; bu sürüm için bu README geçerlidir.

## Çalıştırma

Python 3.10 veya üzeri gerekir. Bağımlılıklar: `pip install -r requirements.txt`.
`OPENAI_API_KEY` sunucunun ortam değişkenlerinde tanımlanmalıdır. Varsayılan model `gpt-5.6-luna` olarak korunmuştur. Anahtar olmadan arayüz ve eğitimler açılır; gerçek AI analizi çalışmaz.

- Üretim: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 240 app_v16_2:app`
- Windows yerel deneme: `.env.example` dosyasını `.env.local` adıyla kopyalayıp kendi anahtarınızı yerelde tanımlayın; `python local_launcher.py` çalıştırın.
- Yerel başlatıcı Python'un yedek HTTP sunucusunu kullanır; dışarıya açılan üretim sunucusu olarak kullanmayın.
- `calibration_profile.json`, `lesson_manifest.json`, `index.html` ve `videos/` aynı proje kökünde kalmalıdır.

## Değişiklikler

- Yorum/sohbet sağlığı için kullanılmayan yedi sınıflı dağılım yerine davranış sinyallerini döndüren uç nokta. Paylaşım niyet–algı analizi ve insan kalibrasyonu korunur.
- Görünmeyen, puanlamada kullanılmayan bağlam-gölge çağrıları kaldırıldı. Yorum/sohbet başına ana işlemler iki paralel istektir; geçici hatalarda mevcut sınırlı tekrar mekanizması korunur.
- Aynı ham çıkarım farklı niyet seçimlerinde tekrar kullanılır. Eşzamanlı aynı istekler birleştirilir; sunucu önbelleğinin geçerliliği beş dakikadır. Profil değişikliği önbellek anahtarını değiştirir.
- Genel sohbet sağlığı aktif ve engellenmemiş sohbetlerin ortalamasıdır; sert test botları da dahildir.
- Bot yanıtı, kullanıcı analizi başarısız olsa da kendi analizine göre ısıyı etkiler.
- Akış ve profil yorum taslakları, odak ve imleç konumu yeniden çizimden sonra korunur.
- Uyum ve yanlış anlaşılma riski yuvarlandığında toplam %100 kalır.
- Video ileri sarma/hızlandırma kapalıdır. Sekme gizlenince durur. Tam izleme ve doğru cevap olmadan eğitim katkısı verilmez. Kapatma düğmesi korunur; erken çıkış tamamlanma sayılmaz.
- Süresi geçmiş geçici eğitim katkısı davranış doğrulamasından önce temizlenir.
- Geçersiz JSON/veri türleri anlaşılır 400 yanıtı verir. Hem Flask hem yerel sunucu yeni sürüm numarasını ve davranış uç noktasını destekler.

## Yükleme

Site güncelleme ZIP'indeki dört kod dosyasını **çalışan uygulamanın mevcut kök dizinindeki karşılıklarıyla birlikte** değiştirin: `index.html`, `run_v16_web.py`, `app_v16_2.py`, `local_launcher.py`. Kalibrasyon ve video dosyalarını silmeyin. Sunucuyu yeniden başlatın veya aynı deployment ayarlarıyla yeniden yayınlayın.

Tam GitHub ZIP'i `NIYET_Final_V12_2026-09-18/` klasörü içerir: kod, 25 video, kalibrasyon, eğitim manifesti, bağımlılıklar, yayın ayarları ve testler. ZIP'i açıp klasörü rapordaki depoya ekleyin. **ZIP dosyasını tek başına depoya yüklemek kaynak dosyalarını güncellemez.** Eski commit değiştirilmez; yeni commit oluşturulur. Önerilen açıklama: `NİYET final V12: analiz çağrıları, sohbet ortalaması ve zorunlu video izleme`.

Yeni klasörü doğrudan deployment kaynağı yaparsanız hizmetin Root Directory ayarını bu klasöre yöneltmeniz gerekir. Mevcut canlı köke küçük güncelleme paketini uyguluyorsanız bu ayarı değiştirmeyin.

## Yayın sonrası doğrulama ve geri dönüş

`/api/status` ve `/healthz` yanıtındaki sürüm `V12-2026-09-18` olmalıdır. `configured: true` ve kalibrasyonun `available: true` olduğunu kontrol edin. Bir niyet analizi, bir yorum, bir özel mesaj ve bir tam video+doğru cevap deneyin. İlk analiz, önbellek yanıtı ve kararlılık/öneri süresini ayrı ölçün.

Yayın öncesi mevcut dört dosyanızı saklayın. Geri dönüş için bunları birlikte geri koyup hizmeti yeniden başlatın. Yeni arayüzü eski sunucuyla birlikte kullanmayın; yeni `/api/analyze_behavior` uç noktası eski sunucuda yoktur.

Bu paket hazırlanırken canlıya yükleme veya GitHub commit/push yapılmamıştır. Yeni sürümün gerçek modelle üretim gecikmesi yayın sonrasında ölçülmelidir. Yerel regresyon testleri kontrollü model yanıtları kullanır; bağımsız insan doğrulaması yerine geçmez.

## Testler ve sınırlar

`python tests/test_backend.py` ve `python tests/test_v12.py`; Node.js ile `tests/*.cjs` dosyalarını ayrı ayrı çalıştırın. Testler için API anahtarı gerekmez. Testler canlı modele istek göndermez.

İzleme kontrolü tarayıcı tabanlıdır: normal arayüzde atlamayı engeller, geliştirici araçlarıyla kötü niyetli müdahaleye karşı sunucu taraflı kimlik/izleme kanıtı değildir. Kullanıcı eğitimden çıkabilir fakat bitirme/puan alamaz. Mobil Safari gibi diğer tarayıcılarda ayrıca kabul testi yapılmalıdır.

Önbellek sunucu belleğinde sınırlı tutulur; bu değişiklik bir mesaj arşivi oluşturmaz. Süresi dolmuş kayıtlar erişim/kapasite tahliyesiyle temizlenir. Mevcut istemci saklama ve dış AI servisine metin iletimi mimarisi değişmemiştir. `.env`, anahtarlar, yerel kullanıcı verileri veya ham anket katılımcı verileri bu pakete dahil değildir.
