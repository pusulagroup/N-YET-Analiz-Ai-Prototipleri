# NİYET V14.4.2 — Anlık Tartışma Isısı ve Sohbet Sağlığı

V14.4.1 video/quiz sürümü temel alınmıştır. 25 gerçek mikro eğitim videosu ve dengeli quiz cevap dağılımı korunurken, kullanıcı etkileşimlerinde gecikmeye yol açan iki kritik davranış akışı ayrıştırılmıştır.

## Başlatma
- Windows: `V14_4_2_BASLAT_WINDOWS.bat`
- macOS/Linux: `V14_4_2_BASLAT_MAC_LINUX.command`
- Python: `python run_v14_4_2.py`
- Varsayılan port: `8856` (doluysa sunucu boş bir sonraki porta geçebilir).

## V14.4.2 kritik düzeltmeleri
- Global `TEST SÜRÜMÜ` etiketi kaldırıldı; normal ürün görünümü kullanılıyor.
- Mikro eğitimlerde `Cevabı kontrol et` düğmesinin önceki tamamlanmış dersten disabled durumda kalabilmesi düzeltildi. Her yeni derste düğme yeniden etkinleşiyor.
- Eski dersin gecikmeli kapanma zamanlayıcısının yeni açılan derse taşınması engellendi.
- Kullanıcının yorumunun Tartışma Isısı artık bot yanıtını/API dönüşünü beklemiyor. Yorum gönderildiği anda yerel davranış katmanı ısı değişimini hesaplıyor ve arayüzü güncelliyor.
- Bot yorumu daha sonra geldiğinde yalnızca bot yanıtının ısı etkisi ayrıca uygulanıyor; kullanıcı yorumuna ikinci kez ısı yazılmıyor.
- Sohbet Sağlığı da aynı şekilde kullanıcının mesajı gönderildiği anda güncelleniyor. Karşı tarafın cevabı geldiğinde yalnızca karşı tarafın davranışı ayrıca işleniyor; çift düşüş engellendi.
- Gölge Niyet/Bağlam Etkisi arka planda çalışmaya devam ediyor ve kullanıcı mesajının gönderilmesini geciktirmiyor.

## Gelişim modülü
- 5 ana alan × 5 konu = 25 gerçek video.
- Her videodan sonra konuya özel tek uygulama sorusu.
- Doğru cevap konumları dengeli: 1. şık 8, 2. şık 9, 3. şık 8.
- Yanlış cevapta öğretici geri bildirim ve tekrar deneme.
- Doğru cevap sonrası tamamlanma ve geçici +3 gelişim katkısı mantığı korunmuştur.

## Davranış akışının yeni sırası
### Yorum
1. Kullanıcı yorumu gönderir.
2. Yerel hızlı davranış analizi anında çalışır.
3. Tartışma Isısı ve kullanıcının NİYET davranış sinyali hemen güncellenir.
4. Bağlam Etkisi ve bot yanıtı arka planda devam eder.
5. Bot yanıtı geldiğinde yalnızca bot yanıtının ısı etkisi eklenir.

### Sohbet
1. Kullanıcı mesajı gönderir.
2. Kullanıcının mesajına bağlı Sohbet Sağlığı anında güncellenir.
3. Bot cevabı arka planda üretilir.
4. Cevap geldiğinde yalnızca karşı tarafın davranışı Sohbet Sağlığına ayrıca yansır.

## Korunan ana özellikler
- İnsan verisiyle kalibre Niyet–Algı analizi.
- Tartışma Yaratma İhtimali, Algı Kararlılığı ve Minimum Müdahale.
- Yorum bazlı Tartışma Isısı.
- Yorum/sohbette Bağlam Etkisi.
- Genç Mod ve yaşa duyarlı müdahale.
- Sohbet Genel mantığı.
- Beş boyutlu özel NİYET Skoru.

## Metodolojik not
Anlık Isı ve Sohbet Sağlığı güncellemesi, botun gelecekte üreteceği cevaba bağlı değildir. Kullanıcının mevcut mesajı yerel ve açıklanabilir davranış sinyalleriyle hemen işlenir; karşı tarafın daha sonra gelen mesajı ayrı bir etkileşim olayı olarak değerlendirilir.
