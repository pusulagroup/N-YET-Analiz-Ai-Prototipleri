# NİYET VFINAL2 — SEO / Google İndeksleme Güncellemesi

VFINAL2 içinde önceki SEO/Google indeksleme yapılandırması korunmuştur.

Eklenenler:
- SEO uyumlu title ve meta description
- `robots` meta etiketi (`index,follow`)
- Canonical URL: `https://niyetaiapp.com/`
- Open Graph ve Twitter meta etiketleri
- SoftwareApplication JSON-LD yapılandırılmış verisi
- `/robots.txt` endpoint'i
- `/sitemap.xml` endpoint'i
- `/api/` yollarının robots.txt üzerinden taramaya kapatılması

Dağıtım:
1. Paket içeriğini mevcut GitHub depo köküne kopyalayın ve aynı adlı dosyaları değiştirin.
2. Commit + push yapın.
3. Render deploy tamamlandıktan sonra şu adresleri kontrol edin:
   - https://niyetaiapp.com/robots.txt
   - https://niyetaiapp.com/sitemap.xml
4. Google Search Console'a `niyetaiapp.com` mülkünü ekleyin.
5. Sitemaps bölümünden `sitemap.xml` gönderin.
6. URL Inspection bölümünde `https://niyetaiapp.com/` için "Request indexing" kullanın.
