# Anket Entegrasyon Notu

V11'de anket sonuçları yalnızca arayüzde istatistik olarak gösterilmez. `calibration_profile.json` içindeki intercept ve 7×15 katsayı matrisi `run_v11.py` tarafından her gerçek Luna analizinde uygulanır.

## Girdi özellikleri

1. 7 Luna niyet/algı olasılığı
2. bu 7 olasılığın doğal logaritmaları
3. Luna dağılımının normalize entropisi

Toplam: 15 özellik.

## Çıktı

7 kategorili insan-algısı soft-label dağılımı:

- Bilgilendirme
- Eleştiri
- İtiraz
- Mizah
- Tavsiye
- Destek / Övgü
- Soru

Ridge çıktısı simplex üzerine projekte edilerek negatif değerler engellenir ve toplam olasılık 1'e / %100'e getirilir.

## Kritik metodoloji

Yazarın seçtiği niyet bu kalibrasyonun girdisi değildir. Bu seçim yalnızca daha sonra kalibre okuyucu dağılımıyla karşılaştırılarak Niyet Kayması üretilmesinde kullanılır.
