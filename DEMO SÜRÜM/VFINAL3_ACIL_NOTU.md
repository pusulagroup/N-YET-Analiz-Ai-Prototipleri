# VFINAL3 ACİL DÜZELTME
- Ön uçtaki 20/35 saniyelik AI timeout kaldırıldı.
- Render yeniden başlatma / Free cold-start sırasında tek başarısız `/api/status` kontrolünün AI'ı kalıcı olarak kapatması önlendi.
- `/api/status` bağlantı gelene kadar 4 saniyede bir sessizce yeniden denenir.
- Ana NİYET analizi, durum rozeti bağlantısız görünse bile gerçek `/api/analyze_fast` endpoint'ini dener.
- Sohbetlerde eski bağlantı bayrağının isteği tamamen engellemesi kaldırıldı; gerçek backend yanıtı esas alınır.
- Arayüzde sürüm adı gösterilmez.
