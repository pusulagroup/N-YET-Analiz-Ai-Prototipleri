# NİYET V14 — Değişiklik Notları

V14 yeni kartlar ekleyerek ana NİYET analizini kalabalıklaştırmak yerine hız, bağlam ve yaşa duyarlı koruma üzerinde yoğunlaşır.

1. **İki aşamalı hızlı NİYET analizi:** Niyet–Algı Uyumu, baskın okuyucu algısı ve yanlış anlaşılma riski önce gösterilir. Algı Kararlılığı ve Minimum Müdahale arka planda tamamlanır.
2. **Daha hafif zenginleştirme:** mikro-varyasyon sayısı azaltıldı, varyant grupları paralel değerlendiriliyor ve aynı mesaj için bellek içi önbellek kullanılıyor.
3. **Minimum Müdahale akışı:** buton adı `Değişikliği uygula ve paylaş` oldu. Önceden doğrulanmış öneri yeniden analiz döngüsüne girmeden doğrudan paylaşılır.
4. **Genç Mod üç iletişim noktasına yayıldı:** paylaşım, yorum ve özel mesaj yazarken yerel ve gecikmesiz koruyucu mikro uyarılar bulunur.
5. **Genç Mod görsel ayrımı:** 18 yaş altı modunda genel arka plan koyu gri, temel yazılar beyazdır.
6. **Yorum Algı Belirsizliği uyarısı:** yorum gönderildikten sonra arka planda analiz edilir; yüksek belirsizlik varsa kısa `Farklı algılanabilir` uyarısı görünür.
7. **Gölge Niyet / Bağlamsal Algı Kayması:** yalnızca yorum ve sohbetlerde, gönderimi geciktirmeden arka planda çalışır. Orta/yüksek durumda küçük `Bağlam Etkisi` kutusu gösterilir.
8. **Sohbet Genel göstergesi sadeleştirildi:** profil fotoğrafının yanında tek küçük kutu bulunur. Skor yalnızca aktif ve engellenmemiş sohbetlerin Sohbet Sağlığı aritmetik ortalamasıdır.
9. **Güvenlik kuralları korunup yeniden bağlandı:** çocukta Tartışma Isısı >50 yorum katılımını kapatır; yetişkinde kullanıcı kaynaklı kritik ısı kilidi korunur; engellenen sohbetler ortalamadan çıkarılır; sohbet güvenlik seçenekleri 5 puanlık yeniden tetikleme mantığını sürdürür.
10. **Regresyon/erişilebilirlik temizliği:** profil tıklamaları, public profil–sohbet–geri akışı, Enter ile gönderim, mobil düzen, koyu tema kontrastı ve API hata yedekleri test kapsamına alındı.

## Gölge Niyet tasarım ilkesi
Gölge Niyet paylaşım oluşturma ekranında **yoktur**. Yorum veya özel mesaj önce normal biçimde gönderilir; bağlamsal analiz sonradan tamamlanır. Düşük bağlam etkisi kullanıcıya ek bir kart olarak gösterilmez.

## Araştırma ilkesi
Yazarın seçtiği niyet, ham okuyucu algısı tahminine verilmez. İnsan kalibrasyon katmanı 450 mesaj × 8 okuyucu = 3.600 bağımsız algı etiketine dayanır. Minimum Müdahale yüzdeleri yalnızca ayrı kör ikinci algı çıkarımı + insan kalibrasyonu sonucunda gösterilir.
