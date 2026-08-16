# NİYET V13.6

- Normal kullanıcıdaki analiz detayları **Ek analiz** olarak sadeleştirildi.
- Ham model dağılımı, ayrı kalibrasyon dağılımı ve uzun araştırma yöntemi metinleri paylaşım analizinden kaldırıldı.
- Ek analizde yalnızca Algı Belirsizliği, Tartışma Tetikleme, Niyet Kayması ve diğer en güçlü üç olası okuyucu algısı tutuldu.
- Normal API yanıtından ham dağılım ve stability-variant araştırma verileri çıkarıldı.
- Özel sohbet botları ağır `reply + iki tam analiz` JSON şemasından ayrıldı; model yalnızca doğal sohbet yanıtı üretir.
- Sohbet Sağlığı için gerekli yapılandırılmış sinyaller hızlı yerel davranış katmanında çıkarılır.
- Geçici sohbet API hatasında sohbetin kilitlenmemesi için açıkça etiketlenen yerel yedek yanıt eklendi.
- Algı Kararlılığı, Minimum Müdahale, skor ve güvenlik mekanikleri korunmuştur.
