# NİYET · Tarihsel Prototipler Birleşik Paket

Bu klasör, NİYET'in daha önce oluşturulmuş prototip sürümlerini **tek bir yerde ve gerekli bağımlı dosyalarıyla birlikte** incelemek için hazırlanmıştır.

## Başlatma

### Windows
`BASLAT_WINDOWS.bat` dosyasına çift tıklayın.

### macOS / Linux
`BASLAT_MAC_LINUX.command` dosyasını çalıştırın veya terminalde `python3 launcher.py` komutunu kullanın.

Başlatıcı tarayıcıda `http://127.0.0.1:8870/` adresini açar. Buradan istediğiniz tarihsel sürümü seçebilirsiniz.

## Paketlenen sürümler

- V1 · İlk Prototip
- V2 · Prototip
- V3 · Prototip
- V4 · Prototip
- V5 · Prototip
- V6.1 · OpenAI
- V7 · Luna
- V8.1 · Luna
- V9 · Luna
- V10 · Luna
- V11 · Anket Entegre
- V12.3 · TEKNOFEST Ana Tema

## Teknik not

V1–V5 tek HTML dosyalı tarihsel prototiplerdir ve katalog sunucusu üzerinden doğrudan açılır. V6.1 ve sonrası bazı sürümler kendi Python backend'ine ihtiyaç duyar; ana başlatıcı bu sunucuları otomatik olarak başlatır ve sürümlere çakışmayan yerel portlar atar.

Ana başlatıcının sürümlere verdiği portlar:

- V6.1 → 8806
- V7 → 8807
- V8.1 → 8818
- V9 → 8819
- V10 → 8820
- V11 → 8830
- V12.3 → 8843

OpenAI kullanan işlevler için geçerli API erişimi gerekebilir. API anahtarını bu klasördeki kaynak dosyalara yazmayın; ilgili sürüm destekliyorsa ortam değişkeni veya sürümün kendi yerel bağlantı akışını kullanın.

## Git / jüri kullanımı açısından önemli not

Bu paket önceki prototiplerin daha sonra tek klasörde toplanmış bir **tarihsel arşividir**. Bu dosyaların Git'e eklendiği tarih, prototiplerin ilk geliştirildiği tarih olarak yorumlanmamalıdır. Repo açıklamasında bunların Git sürüm kontrolüne geçilmeden önce oluşturulup ayrı dosyalar halinde korunan tarihsel sürümler olduğu açıkça belirtilmelidir.

Ana başlatıcı (`launcher.py`) yalnızca sürümleri düzenli biçimde açmak için eklenmiştir; tarihsel prototip kaynaklarının içeriğini değiştirmez.
