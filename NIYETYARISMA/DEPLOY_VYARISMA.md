# VYARISMA — GitHub + Render güncelleme

1. `VYARISMA_GITHUB_GUNCELLEME.zip` dosyasını aç.
2. İçindeki dosyaları mevcut `niyet-v16` repo klasörünün üzerine kopyala.
3. Çalışan `videos/` klasörüne dokunma.
4. GitHub Desktop → Summary: `VYARISMA final release`
5. `Commit to main`.
6. `Push origin`.
7. Render otomatik deploy olmazsa `Manual Deploy` → `Deploy latest commit`.
8. Render Start Command:
   `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 240 app_vyarisma:app`
9. Site açıldığında üstte `YARIŞMA SÜRÜMÜ` gör.
10. Son test: analiz, yorum/Tartışma Isısı, Sohbet, Skorum ve bir Gelişim videosu.
