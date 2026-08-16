# NİYET V13 Değişiklik Notları

## Ana yenilikler
- Algı Kararlılığı: kontrollü mikro-varyasyonların kör ikinci algı çıkarımı ve insan kalibrasyonu ile karşılaştırılması.
- Minimum Müdahale: kullanıcı niyetine göre minimal aday üretimi, ardından adayların ayrı kör algı çıkarımıyla gerçek yeniden ölçümü.
- Niyet bazlı paylaşım öncesi iletişim rehberi.
- Normal kullanıcı analiz ekranının sonuç → neden → müdahale sırasına göre sadeleştirilmesi; ham model detaylarının açılır teknik bölümde tutulması.

## Regresyon ve profil düzeltmeleri
- Avatar, kullanıcı adı ve kullanıcı etiketi tek profil yönlendirme fonksiyonuna bağlandı.
- Yorumlardaki kendi kullanıcı profili dahil tüm profil tıklamaları tutarlı hale getirildi.
- Üst çubuktaki kullanıcı alanı kendi profile bağlandı.
- Public profile → sohbet → geri akışı aynı profile dönecek şekilde düzenlendi.
- Profil kapağı/avatar negatif yerleşimi, z-index, overflow ve responsive boyutlar güçlendirildi.
- Paylaşım görsellerinde kontrollü 16:9 alan ve object-fit davranışı eklendi.

## Korunan V12.4 davranışları
- Yorum bazlı dinamik Tartışma Isısı.
- Her yorumda heatBefore / heatAfter / heatDelta.
- Sert yorumların ısıyı yanlışlıkla düşürmesini engelleyen güvenlik tabanı.
- Isıya bağlı mavi → açık kırmızı → açık bordo yorum kutusu geçişi.
