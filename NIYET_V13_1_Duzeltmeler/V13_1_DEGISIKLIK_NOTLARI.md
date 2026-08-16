# NİYET V13.1 Değişiklik Notları

## Algı analizi düzeltmeleri
- Minimum Müdahale artık yalnızca pozitif niyet uyumu kazancı olan adayları göstermiyor; adaylar ayrıca belirsizlik artışı, yeni baskın algı sapması ve değişiklik maliyeti açısından güvenlik filtresinden geçiriliyor.
- Tüm adaylar kötüleşiyorsa sistem olumsuz öneriyi göstermiyor ve “Güvenilir minimal iyileştirme bulunamadı” sonucunu veriyor.
- Aday sayısı 3'ten 5'e çıkarıldı; kullanıcıya en fazla 3 güvenli aday gösteriliyor.
- Algı Belirsizliği, insan-kalibre dağılımlarda entropinin doğal yüksekliğini yanlış yorumlamamak için yeniden tanımlandı. Yeni skor en güçlü iki algının yakınlığını ana sinyal, dağılım yayılımını yardımcı sinyal olarak kullanıyor.
- Minimum Müdahale kartında öneri öncesi/sonrası Algı Belirsizliği de gösteriliyor.

## Sohbet Sağlığı ve yaşa duyarlı müdahale
- Tekrarlayan zararlı konuşmalarda Sohbet Sağlığı daha hızlı düşecek şekilde güncelleme katsayıları güçlendirildi.
- Sohbet Sağlığı hesabında riskli tarafın etkisi %85, diğer tarafın etkisi %15 olarak ağırlıklandırıldı.
- 18 yaş altı modda Engelle / Sohbete devam et / Ebeveyne veya güvendiğin yetişkine yönlendir seçenekleri 50/100 ve altında açılıyor.
- Standart kullanıcıda Engelle / Sohbete devam et seçenekleri 30/100 ve altında açılıyor; yetişkine yönlendirme gösterilmiyor.
- “Sohbete devam et” seçildiğinde aynı uyarı sürekli tekrarlanmıyor; sağlık 5 puan daha düşerse seçenekler yeniden açılıyor.

## Tartışma Isısı düzeltmeleri
- Isı etiketi her yorumda doğrudan `heatAfter - heatBefore` farkından yeniden hesaplanıyor; görüntü sırası `önce → sonra · değişim` olarak sabitlendi.
- Örnek: `Isı 10 → 47 · +37`.
- Kullanıcının kendi yorumu Tartışma Isısını 80/100 veya üzerine çıkarırsa anlık uyarı gösteriliyor ve o paylaşım için yeni yorum gönderme kapatılıyor.
- Eşik aşılırsa otomatik karşı yorum eklenmeyerek tartışmanın daha da uzatılması önleniyor.

## V13'ten korunanlar
- Algı Kararlılığı: kontrollü mikro-varyasyonların kör ikinci algı çıkarımı ve insan kalibrasyonu ile karşılaştırılması.
- Minimum Müdahale: adayların ayrı kör algı çıkarımıyla gerçek yeniden ölçümü.
- Niyet bazlı paylaşım öncesi iletişim rehberi.
- Profil yönlendirme, avatar/kapak taşma ve responsive düzeltmeleri.
- Isıya bağlı mavi → açık kırmızı → açık bordo yorum kutusu geçişi.
