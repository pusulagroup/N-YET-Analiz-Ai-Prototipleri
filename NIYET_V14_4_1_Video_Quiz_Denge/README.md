# NİYET V14.4.1 — Video Entegre Quiz Denge Sürümü

V14.4 video entegre sürümü temel alınarak hazırlanmıştır. Ana sosyal yapay zekâ akışı korunurken Gelişim ekranına kullanıcı tarafından hazırlanan 25 gerçek mikro eğitim videosu ve her konuya özgü tek soruluk kısa uygulama testi entegre edilmiştir.

## Başlatma
- Windows: `V14_4_1_BASLAT_WINDOWS.bat`
- macOS/Linux: `V14_4_1_BASLAT_MAC_LINUX.command`
- Python: `python run_v14_4_1.py`
- Varsayılan port: `8855` (doluysa sunucu boş bir sonraki porta geçebilir).

## V14.4.1 düzeltmesi
- 25 mikro eğitim quizindeki doğru cevap konumları dengeli biçimde çeşitlendirildi.
- Doğru cevaplar artık sürekli aynı şıkta değildir: 1. şık 8, 2. şık 9, 3. şık 8 soruda doğrudur.
- Soru metinleri, doğru cevap içerikleri, öğretici açıklamalar ve video eşleşmeleri değiştirilmedi.
- Amaç, cevap konumundan öğrenilebilecek örüntüyü kaldırarak quiz deneyimini daha güvenilir kılmaktır.

## Gelişim modülü
- 5 ana alan × 5 konu = 25 gerçek video.
- Dosya sırası 1–25, NİYET eğitim konu sırasıyla birebir eşleştirilmiştir.
- Her video yaklaşık 10 saniyedir.
- Video tamamlanınca konuya özel 1 çoktan seçmeli uygulama sorusu açılır.
- Yanlış cevapta kısa öğretici açıklama gösterilir; kullanıcı tekrar deneyebilir.
- Doğru cevap sonrası eğitim tamamlanmış sayılır.
- Tamamlanan dersler tarayıcıda yerel olarak saklanır ve Gelişim ekranında `x / 25 tamamlandı` olarak gösterilir.
- Mevcut +3 gelişim katkısı mantığı korunmuştur: katkı geçicidir ve sonraki gerçek davranışlarla doğrulanması gerekir.

## Eğitim alanları
1. Saygı — 1–5
2. Yapıcılık — 6–10
3. Tutarlılık — 11–15
4. Gerilim Yönetimi — 16–20
5. İletişim Açıklığı — 21–25

## Korunan ana V14 özellikleri
- İnsan verisiyle kalibre Niyet–Algı analizi.
- Tartışma Yaratma İhtimali, Algı Kararlılığı ve Minimum Müdahale.
- Yorum bazlı Tartışma Isısı.
- Yorum/sohbette Bağlam Etkisi (Gölge Niyet).
- Genç Mod ve yaşa duyarlı koruyucu müdahaleler.
- Sohbet Sağlığı / Sohbet Genel mantığı.
- Beş boyutlu özel NİYET Skoru.

## Not
Bu sürümde bağımsız anket sonuçları henüz nihai ürün kurallarına geri beslenmemiştir. Anketler tamamlandıktan sonra yalnızca gerekli son düzeltmeler yapılmalı, ardından final sürüm dondurulup performans/erişilebilirlik/regresyon testleri çalıştırılmalıdır.
