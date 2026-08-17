# NİYET V14.1 Test Notları

## Tartışma Isısı
- Nötr/kibar örnek analiz (`is_polite=true`, `has_reasoning=true`) => delta `0`.
- Açık sakinleştirme (`is_calming=true`) => negatif delta.
- Kovucu/saldırgan davranış => pozitif delta ve mevcut minimum artış kuralları korunur.

## Gölge Niyet
Mock regresyon testi:
- Bağlam: `Farklı fikirlerin aynı ortamda kalabilmesi...`
- Yorum: `makarna tuzu iyi mi sence???😂😂`
- `context_relevance=12`, `context_dependency=false` => **Bağlam Etkisi: Düşük** (dağılımlar farklı çıksa bile konu dışılığı bağlam etkisi sayılmaz).

Kontrol örneği:
- Bağlam: `Bu fikrin hiçbir mantıklı tarafını göremiyorum.`
- Yorum: `aynen kanka 😂`
- yüksek bağlam ilişkisi + bağlama bağımlılık => **Bağlam Etkisi: Yüksek**.

## Sohbet Genel Skoru
Normal sosyal persona sayısı: 20.
- 19 sohbet = 100
- 1 sohbet = 33
- `(19×100 + 33) / 20 = 96,65` => arayüzde **97/100**.
- Engellenmiş normal hesap paydadan çıkarılır.
- Güvenlik-test botları genel profile dahil edilmez.

## Teknik
- Python `py_compile`: geçti.
- JavaScript `node --check`: geçti.
- `/api/status`: `version=14.1`, `human_labels=3600` doğrulandı.
