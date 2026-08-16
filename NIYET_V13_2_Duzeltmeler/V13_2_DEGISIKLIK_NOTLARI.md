# NİYET V13.2 Değişiklik Notları

## Analiz ve öneri akışı
- Minimum Müdahale kartları tavsiye-only hale getirildi.
- Otomatik metin değiştirme kaldırıldı.
- Öneri sonrasında otomatik yeniden analiz kaldırıldı; öneri döngüsü kapatıldı.
- Niyet Kayması, Niyet–Algı Uyumu, Algı Belirsizliği ve Algı Kararlılığı merkezi skorun İletişim Açıklığı hedefinde birlikte ele alındı.
- 3.600 insan etiketi doğrudan kişisel puan değildir; algı sinyallerinin güven katsayısında kullanılır.

## Merkezi NİYET Skoru
- 25/20/20/20/15 alan ağırlıkları korundu.
- Kamusal paylaşım ve yorum üslubu davranış alanlarını kademeli günceller.
- Özel sohbetlerde yalnızca kullanıcının kendi yapılandırılmış davranış sinyalleri düşük ağırlıkla alanlara yansır.
- Karşı tarafın saldırganlığı kullanıcının NİYET skorunu düşürmez.
- NİYET skorunun altında Sohbet Sağlığı Ortalaması eklendi.
- Kullanıcı profilinde Sohbet Genel Skoru ve Sohbet Sağlığı Ortalaması eklendi.

## Sohbet güvenliği
- 18+ Standart Mod güvenlik buton eşiği 50/100 olarak düzeltildi.
- Eşik altındaki butonların risk etiketi bulunmadığında kaybolmasına neden olan koşul kaldırıldı.
- 18 yaş altı modda eşik 50/100; yetişkine yönlendirme yalnızca bu modda bulunur.
- “Sohbete devam et” sonrası yeniden açılma noktası ham sağlık değeri üzerinden `-5` olarak kaydedilir ve eşik geçildiğinde durum sıfırlanır.

## Tartışma Isısı
- Bütün başlangıç Tartışma Isıları 10/100 olarak sabitlendi.
- 18 yaş altı modda Isı >50 olduğunda yorum katılımı kapatıldı.
- 18+ için kullanıcının kendi yorumu Isıyı >=80 yaptığında mevcut kilit davranışı korunur.
- Isı değişimi önce → sonra + delta mantığıyla saklanır/gösterilir.

## UI
- Üst `Ara` kutusu kaldırıldı.
- Yanıt placeholder'ı `Yanıt yaz...` olarak sadeleştirildi.
- Yorum kutularında Enter ile gönderim eklendi; sohbet Enter davranışı korundu.
