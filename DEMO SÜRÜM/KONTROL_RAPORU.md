# NİYET — ayrıntılı kontrol ve düzeltme raporu

Tarih: 18 Eylül 2026. Hazırlanan sürüm: **V12-2026-09-18**.

**Sonuç:** Dünkü canlı kontroller tamamlayıcı API ölçümleriyle genişletildi; saptanan gecikme kaynakları ve işlev hataları için güncelleme paketi hazırlandı. Yerel regresyon testleri geçti. **Paket canlıya yüklenmedi ve GitHub'a gönderilmedi.** Dolayısıyla aşağıdaki canlı ölçümler mevcut V11'e, yeni davranış testleri V12 paketine aittir. Yeni sürümün canlı model gecikmesi henüz ölçülmüş değildir.

## 1. Canlı sürüm ve rapordaki depo

- Kontrol edilen site: https://www.niyetaiapp.com/
- Teknik rapordaki depo: https://github.com/pusulagroup/N-YET-Analiz-Ai-Prototipleri
- Canlı HTML, yereldeki V11 dosyasıyla SHA-256 düzeyinde eşleşti: `fd19b0c670c2a48f57573a6d9d2634066c7bfd96966aeec1e30d6d50ed44cd25`.
- Canlı arayüzde V11'in sert sohbet başlangıçları bulundu. Buna karşın durum uç noktası hâlâ eski `VFINAL3` etiketini döndürüyor. Bu nedenle yalnızca bu etikete bakarak “V11 yok” demek yanlış olur.
- Sunucu kaynak dosyalarının birebir aynı olduğu yalnızca HTTP üzerinden ispatlanamaz. Arayüz eşleşmesi ile API davranış kontrolleri ayrı kanıtlardır.
- Depodaki `sonun sonu final v3`, `Yeni klasör` ve `Vson_surum` kaynakları karşılaştırıldı; kodları mevcut canlı V11 ile aynı değil. İncelenen kalibrasyon içerikleri satır sonu normalizasyonundan sonra eşleşiyor.
- V12'de hem Flask hem yerel yedek sunucu artık aynı açık sürüm numarasını döndürüyor. Yükleme sonrasında `/api/status` → `V12-2026-09-18` görülmeli.

## 2. Gecikme: gerçekten ne ölçüldü?

Ölçümler bu bilgisayardan uçtan uca HTTP süresidir; ağ ve servis kuyruğu dahildir. Küçük örneklemdir, kapasite testi veya p95 değildir.

| İşlem | Ölçülen mevcut canlı süre | Açıklama |
|---|---:|---|
| 17 Eylül, 10 farklı ilk analiz | 2,07–4,22 sn | Önbelleksiz temel analiz örnekleri |
| 18 Eylül, 5 farklı ilk analiz | 2,75–5,10 sn | Ortalama 3,56 sn |
| 18 Eylül, aynı sorunun tekrarı | 0,157 sn | Önbellekten yanıt |
| 17 Eylül, bot yorumları | 3,09–3,48 sn | Üç persona, yanıt ve yanıt davranışı |
| 17 Eylül, sohbet yanıtları | 2,70–3,36 sn | Beş kısa sohbet turu |
| Kararlılık / öneri ikinci aşaması | Örneklerde 2,57–9,09 sn | Temel sonuçtan sonra tamamlanan ayrı aşama |

“Analiz yaklaşık üç saniye” tek başına yeterli bir açıklama değil: ilk model çağrısı, önbellek yanıtı ve ikinci aşama ayrı değerlendirilmelidir. İkinci aşamanın temel analize eklenmesi bazı örneklerde toplam beklemeyi belirgin artırıyor. Bu aşama temel sonucun ekrana gelmesini engellememelidir; mevcut iki aşamalı gösterim korunmuştur.

### Uygulanan hız düzeltmeleri

1. Yorum/sohbet sonrasında görünmeyen ve puanlamada kullanılmayan `context_shadow` isteği kaldırıldı. Normal başarılı turda üç uygulama isteği yerine iki istek kalır; hata tekrarları bunun dışındadır. Açık bağlam analizinin sunucu işlevi silinmedi.
2. Yorum ve sohbet sağlığı için yalnızca gerekli davranış alanlarını üreten `/api/analyze_behavior` eklendi. Bu akışlarda seçilmiş yazar niyeti zaten bulunmuyordu; niyet–algı dağılımı ekranda kullanılmıyordu. Paylaşım analizi tam yedi sınıflı dağılımı ve insan kalibrasyonunu kullanmaya devam eder.
3. Aynı metin/bağlam/model için kör ham çıkarım yeniden kullanılabiliyor. Kullanıcı yalnızca seçtiği niyeti değiştirdiğinde yeni model çağrısı gerekmez; karar katmanı yeni seçime göre yeniden hesaplanır.
4. Eşzamanlı aynı istekler tek çıkarımda birleştirilir. Sekiz aynı paralel isteğin tek hesaplamayı paylaşması kontrollü testte doğrulandı. Hata olursa bekleyen işlem kaydı temizlenir; sonraki deneme kilitlenmez.
5. Sunucu önbelleğine beş dakikalık geçerlilik ve tam kalibrasyon profili parmak izi eklendi. Profil değişirse eski karar sonucu yeniden kullanılmaz.
6. Otomatik bot yorumunda boş kullanıcı metni için gereksiz kullanıcı analizi istenmiyor; yalnızca yanıt ve yanıtın davranışı üretiliyor.

**Kazanım sınırı:** İstek sayısının azalması ve tekrarların önlenmesi test edildi. Yeni davranış şemasının gerçek modelde kaç milisaniye kazandırdığı ve ürettiği bayrakların doğruluğu yerelde API anahtarı olmadığı için ayrıca canlı modele karşı ölçülemedi. “Artık her analiz bir saniye” gibi bir iddia yapılmıyor. Model değiştirilmedi, kalibrasyon katsayıları değiştirilmedi ve doğrulanmamış ifade önerileri hız uğruna gösterilmedi.

## 3. Niyet–algı ve Türkçe ayrımlar

Canlı örneklerde aşağıdaki ayrımlar beklentiyle uyumluydu:

| Örnek | Canlı gözlem |
|---|---|
| “Sen malsın.” | Hakaret ve kişisel saldırı algılandı |
| “Bugün dükkâna yeni mal aldım.” | Hakaret/kişisel saldırı işaretlenmedi |
| “Sen aptalsın, burada konuşma.” | Hakaret ve kişisel saldırı algılandı |
| “Sen aptal değilsin, kendini suçlama.” | Hakaret işaretlenmedi; olumsuzlama korundu |
| “Bana aptal demen doğru değil; kişisel saldırı yapma.” | Alıntılanan hakaret yazara mal edilmedi |
| Gerekçeli fikir eleştirisi | Kişisel saldırı işaretlenmedi |
| Özür ve sakin konuşma çağrısı | Hakaret işaretlenmedi |

Emoji ve tekrarlı noktalama örneklerinde kararlılık varyasyonları üretildi. Her cümlede anlamı koruyan küçük bir varyasyon bulunması garanti değil. Varyasyon bulunmadığında eski “Hesaplanamadı” etiketi bir servis arızası sanılabiliyordu; V12 bunu “Uygun küçük varyasyon yok” olarak ayırır. Gerçek servis hatası yine başarısızlık olarak kalır.

Niyet uyumu ile yanlış anlaşılma riskinin ayrı ayrı yuvarlanması ekranda `%29 + %72` gibi toplam %101 oluşturabiliyordu. Gösterim düzeltildi; risk, gösterilen uyumun 100'e tamamlayıcısıdır. Sunucu hesaplarının hassasiyeti korunur.

Kalibrasyon için 1.000 rastgele dağılımda toplam, negatif olmama ve uyum/risk tamamlayıcılığı test edildi. Eksik/bozuk profilin sessizce geçerli kalibrasyon gibi sunulmaması da test edildi. Bunlar matematik/işlev testleridir; yeni bir doğruluk oranı ölçümü değildir.

## 4. Tartışma ısısı ve sohbet sağlığı

- Kullanıcı analizi ile bot cevabı aynı anda başlıyor. Kullanıcı puanı bot cevabını beklemiyor. Bot yanıtının puanlama sırası, kullanıcı etkisinden sonra korunuyor; bu nedenle botun ekranda görünmesi yavaş kullanıcı analizinden etkilenebilir.
- Kullanıcı analizi başarısız olsa bile başarılı bot cevabının kendi ısı etkisi artık uygulanıyor. Daha önce yorum akışında bu etki kullanıcının başarılı analizine bağlıydı.
- Başarısız analiz, sahte “nötr/sağlıklı” puana çevrilmiyor; yorum korunuyor ve hata durumu gösteriliyor.
- Sakinleştiren botun alıntıladığı sert sözler kendisinin hakareti sayılmamalı: mevcut yanıt/alıntı ayrımı regresyon testlerinden geçti. Önceki “açıklayıcı bot mesajı +30 ısı ekliyor” türü örnek için kontrollü test korunuyor.
- Mevcut ısı ve sohbet sağlığı ağırlıkları değiştirilmedi. Sert başlangıç botları korundu; başlangıç mesajları gerçekten sohbet sağlığına etki ediyor.
- Genel sohbet skoru önemli bir gösterim hatası içeriyordu: aktif sert sohbetler düşerken kullanılmamış normal botların 100 değerleri / test botlarının dışlanması genel sonucu 100'de tutabiliyordu. Artık aktif ve engellenmemiş sohbetler dahil edilir. V12 arayüzünde iki sert başlangıç sohbetiyle **genel skor 78**, kullanıcının kendi davranış ortalaması **100** görüldü. Karşı tarafın saldırganlığı kullanıcının kişisel davranışı gibi cezalandırılmıyor.
- Sert botların iki başlangıç mesajı, tekrar eklenmeme, engelli kişiye başlangıç eklememe ve her mesajdaki sağlık etkisi test edildi.

## 5. Yorumlar, profil ve genç modu

- Aynı paylaşım akışta ve profilde göründüğünde yorum alanlarının kimlikleri tekrarlanabiliyor. V12 taslakları ekran bazında korur; son yeniden çizimden sonra odak ve imleç de geri konur. Ayrı akış/profil taslaklarıyla test edildi.
- Yeni oluşturulan kendi paylaşımının `findPost` ile bulunması ve ortak yorum akışının başarı/hata durumları test edildi. Yeni V12 ile gerçek model kullanan uçtan uca yayınla→yorum yap denemesi yapılamadı; bu doğrulamayı tamamlanmış gibi saymıyorum.
- Yerel tarayıcıda genç modu seçildiğinde ısısı 58 olan zincirlerde yorum gönderme düğmeleri kapandı ve 50 eşiği açıklaması göründü. İçeriği okuma korunuyor.
- Beğeni, paylaşım, profil ve sohbet görünümlerinin kaynakları korunmuştur; tüm cihaz/tarayıcı kombinasyonlarında kapsamlı kabul testi yapılmış değildir.

## 6. Mikro eğitim: izlemeyi atlama kapatıldı

Yeni davranış:

- İleri sarma çubuğu ve hız seçimi gösterilmez; oynatma hızı 1× tutulur.
- İzlenmemiş bir zamana sıçrama engellenir. Yalnızca `ended` olayı gelmesi tamamlanma için yeterli değildir.
- Gerçek oynatma süresi ve ulaşılan izleme noktası birlikte takip edilir. Sekme gizlenirse video durur.
- Kullanıcı duraklatabilir ve devam edebilir. Pencereyi kapatabilir fakat tamamlanma ve puan alamaz; yeniden açınca baştan izler.
- Tam izleme sonrası soru açılır. Yanlış cevap katkı vermez. Doğru cevap +3 geçici katkının mevcut koşullarını uygular.
- Süresi geçmiş geçici katkı, davranışla doğrulanmadan önce temizlenir. İki uygun davranışın doğrulaması ve süre aşımı test edildi.

Gerçek yerel tarayıcıda ilk video başında soru görünmedi; normal izleme sonunda `%100` ve soru göründü. Yanlış cevap tamamlamadı; doğru cevap `1/25` ve `+3 geçici katkı` oluşturdu. Kod düzeyinde sona sıçrama, hızı artırma, sekme gizleme, erken soru tamamlama çağrısı ve yeniden açma temizliği test edildi. Tüm 25 videonun dosya erişimi ve HTTP Range yanıtları kontrol edildi; 25 videonun her biri baştan sona görsel olarak izlenmedi.

**Sınır:** Bu, normal kullanıcı arayüzünde atlamayı engeller. Tarayıcının geliştirici araçlarını kullanan kişinin istemci durumunu değiştirmesini kesin olarak engellemez. Sunucu taraflı kullanıcı hesabı ve eğitim kanıtı mevcut prototipte yoktur. Kullanıcının pencereden çıkmasını zorla engellemek yerine, çıkışın tamamlanma sayılmaması sağlandı.

## 7. Test kapsamı ve kanıtlar

| Denetim | Sonuç |
|---|---|
| Eski davranışları koruyan Python regresyonları | 28 test geçti |
| V12 önbellek, eşzamanlılık, tür denetimi, yerel sunucu ve dosya testleri | 11 test geçti |
| Yorum/sohbet paralel başlama, farklı bitiş sırası, bağımsız hata, tek puanlama | 9 senaryo geçti |
| Niyet analizi istemci önbelleği, bağlam ayrımı, hata ve eski yanıt koruması | 7 kontrol geçti; test edilen parçaların yeni kaynakla eşleşmesi kontrol edildi |
| Sağlık hesapları ve sert bot başlangıçları | Node regresyonları geçti |
| Video, taslak/imleç, aktif ortalama, yeni paylaşım erişimi, eğitim katkısı | Node kontrolleri geçti |
| Python ve satır içi JavaScript sözdizimi | Geçti |
| 25 yerel video | Hepsi 206 Range yanıtı verdi |
| Gizli dosya/kaynak dosyası için kamuya açık yollar | Test edilen yollar 404; API anahtarı değiştirme yolu 403 |

Kanıt kayıtları `audit-2026-09-18/regression-results.json` ve `audit-2026-09-18/live-recheck.json` dosyalarındadır. Önceki canlı testler `audit-2026-09-17/live-results.json`, `followup-results.json` ve `repo-comparison.json` içindedir. API testlerinde kullanılan metinler bu denetim için oluşturulmuş örneklerdir.

Yerel otomatik testler kontrollü model yanıtları kullanır. Yeni davranış uç noktasının canlı anlamsal kalite testi, mobil Safari/Android medya davranışı, uzun süreli çok kullanıcılı yük testi ve üretim yayını sonrası ölçüm bu raporun tamamlanmış kapsamına dahil değildir. “Tüm sistem hatasızdır” sonucu çıkarılamaz.

## 8. Teslim paketleri

**NIYET_Site_Guncelleme_V12_2026-09-18.zip**: Mevcut çalışan siteye uygulanacak dört güncel kod dosyası ve yükleme notları. Mevcut videoları ve kalibrasyonu silmeden dosyaları birlikte değiştirin, sunucuyu yeniden başlatın.

**NIYET_GitHub_Tam_Proje_V12_2026-09-18.zip**: Depoya yeni güncel sürüm olarak eklenebilecek tam proje klasörü. 25 video, kalibrasyon, eğitim manifesti, kod, bağımlılıklar, yayın ayarı, dokümantasyon ve taşınabilir testler içerir. Eski prototiplerin tamamını tekrar indiren bir depo yedeği değildir; güncel projenin tam dosya paketidir. Commit ancak bu klasör depoya eklendiğinde oluşur.

ZIP'lerde `.env`, gerçek API anahtarı, kullanıcı sohbetleri, Python önbellekleri ve yerel bağımlılık klasörleri bulunmaz. Boş `.env.example` tam projede vardır. Paket bütünlüğü dosya hash listeleriyle denetlenir.

Yükleme sonrası ilk kontrol: `/api/status` sürüm, API yapılandırması ve kalibrasyon bilgisi. Ardından niyet analizi, yorum, özel mesaj ve tam video+doğru cevap akışı. Gerçek V12 gecikme karşılaştırması aynı metinlerle ve ilk/tekrar/ikinci aşama ayrı ölçülerek yapılmalıdır.
