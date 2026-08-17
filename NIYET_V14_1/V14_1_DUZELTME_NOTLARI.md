# NİYET V14.1 Düzeltme Notları

1. **Tartışma Isısı nötr yorum koruması**
   - Yalnızca kibar, gerekçeli veya nötr olmak ısı düşüşü üretmez.
   - Negatif delta için açık özür, sakinleştirme veya karşı tarafı saygılı biçimde kabul etme gerekir.

2. **Gölge Niyet bağlam ilgisi kapısı**
   - `context_relevance` (0-100) ve `context_dependency` sinyalleri eklendi.
   - Konu dışı/rastgele yorumlarda bağlam etkisi zorla yükseltilmez.
   - Konu uyuşmazlığı ile bağlam kaynaklı anlam değişimi ayrıldı.

3. **Sohbet Genel Skoru**
   - Tüm normal botlar, hiç konuşulmamışsa 100 başlangıç değeriyle ortalamaya girer.
   - Engellenmiş hesaplar ortalamadan çıkarılır.
   - Güvenlik-test botları profilin genel sohbet ortalamasını etkilemez.
