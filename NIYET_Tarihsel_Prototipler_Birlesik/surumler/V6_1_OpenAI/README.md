# NİYET V6.1 — gerçek OpenAI sohbet bağlantısı

## Windows
1. ZIP dosyasını **tamamen çıkartın**.
2. `V6_1_BASLAT_WINDOWS.bat` dosyasına çift tıklayın.
3. Tarayıcı otomatik açılır. Sohbet sekmesinde **OpenAI API'yi Bağla** penceresi görünür.
4. OpenAI API anahtarınızı bu yerel pencereye girin. Model varsayılan olarak `gpt-5.6`.
5. Bağlantı başarılı olduğunda üstte **OpenAI bağlı** görünür ve bot mesajları gerçek API'den gelir.

## Mac / Linux
`V6_1_BASLAT_MAC_LINUX.command` çalıştırın veya terminalde `python3 run_v6.py` yazın.

## Güvenlik
API anahtarı HTML dosyasına veya localStorage'a yazılmaz. Yalnızca çalışan Python sürecinin belleğinde tutulur. Sunucuyu kapattığınızda anahtar unutulur.

## Önemli
ChatGPT Plus/Pro aboneliği API kullanımı sağlamaz. OpenAI API hesabında ayrıca API erişimi ve gerekli ödeme/bakiye ayarı bulunmalıdır.
