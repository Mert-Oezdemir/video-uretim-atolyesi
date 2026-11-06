# Depoda çalışan ajanlar

- `README.md` içindeki komutları depo kökünden çalıştır. CLI'daki `JOB`, iş klasörünü gösterir. `--input`, `--plan`, `--overlays` ve `--captions` yolları o iş klasörüne göredir.
- Ham kaydı ve ham transkripti koru. Kesim adaylarını kaynak zamanına göre öner. Onaylı kesimi değiştiren bir revizyondan sonra altyazıyı yeniden üret veya aynı kesim planıyla yeniden zamanla.
- Altyazı, sahne grafiği ve bölüm zamanlarını `cut/locked.mp4` üzerinden hesapla. Eksik kaynak veya zaman kodu varsa bunu belirt. Ürün sürümü, sayı, ölçüm ya da kaynak uydurma.
- Her sahne için kullanılacak dosyayı ve doğru zaman aralığını kaydet. Grafik ve başlık metnini kaynakla karşılaştır. Sahne düzenini 16:9 ve 9:16 için ayrı değerlendir.
- Önce önizleme üret. Kullanıcıdan kesim, sansür, ses senkronu ve okunurluk kararını al. Final render veya dış platforma yayın için kullanıcı talimatına göre ilerle.
- Yerel üretim dosyalarını, ham medyayı, özel notları ve anahtarları Git'e ekleme. Bir bulut sağlayıcısına medya göndermeden veya ücretli üretim başlatmadan önce hangi içeriğin gideceğini ve tahmini maliyeti kontrol et. Kullanıcının açık yetkilendirmesini kullan.
- Kod değişikliklerinde ağ gerektirmeyen sentetik demoyu doğrula. Gerçek Whisper, Topview, Playwright veya HyperFrames testi yapılmadıysa o entegrasyonu doğrulanmış diye sunma.
