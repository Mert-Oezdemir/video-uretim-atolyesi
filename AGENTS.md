# Depoda çalışan ajanlar

Yerel tek ajan akışı şu sırayı izler. Önce `doctor` ve `init` çalıştır. Ham kayıt yalnızca ses içeriyorsa veya görüntü ve anlatım ayrıysa `prepare` kullan. Ham transkripti oluştur, `plan --engine codex` veya `plan --engine claude` ile aday kesim hazırla. Kullanıcı aday kesimi onaylayınca `run JOB --plan plans/cut.candidate.json` ile önizleme üret. Gerekli grafik ve ses revizyonlarını uygula. Kullanıcı önizlemeyi onayladığında aynı ayarlarla `--final` ekleyip yayın paketini üret. Kaydın tamamı korunacaksa `--keep-all` seç. `run --language` teslimdeki ana altyazının dilini de belirler.

- `README.md` içindeki komutları depo kökünden çalıştır. CLI'daki `JOB`, iş klasörünü gösterir. `--input`, `--plan`, `--overlays` ve `--captions` yolları o iş klasörüne göredir.
- Ham kaydı ve ham transkripti koru. Kesim adaylarını kaynak zamanına göre öner. Onaylı kesimi değiştiren bir revizyondan sonra altyazıyı yeniden üret veya aynı kesim planıyla yeniden zamanla.
- Altyazı, sahne grafiği ve bölüm zamanlarını `cut/locked.mp4` üzerinden hesapla. Eksik kaynak veya zaman kodu varsa bunu belirt. Ürün sürümü, sayı, ölçüm ya da kaynak uydurma.
- Her sahne için kullanılacak dosyayı ve doğru zaman aralığını kaydet. Grafik ve başlık metnini kaynakla karşılaştır. Sahne düzenini 16:9 ve 9:16 için ayrı değerlendir.
- Önce önizleme üret. Kullanıcıdan kesim, sansür, ses senkronu ve okunurluk kararını al. Final render veya dış platforma yayın için kullanıcı talimatına göre ilerle.
- Yerel üretim dosyalarını, ham medyayı, özel notları ve anahtarları Git'e ekleme. Bir bulut sağlayıcısına medya göndermeden veya ücretli üretim başlatmadan önce hangi içeriğin gideceğini ve tahmini maliyeti kontrol et. Kullanıcının açık yetkilendirmesini kullan.
- Kod değişikliklerinde ağ gerektirmeyen sentetik demoyu doğrula. Gerçek Whisper, Topview, Playwright veya HyperFrames testi yapılmadıysa o entegrasyonu doğrulanmış diye sunma.


## Blender + Higgsfield ajan yönlendirmesi

İstek **kodla 3D/video animasyonu, Blender MCP, Codex bağlantısı, Higgsfield, ürün-patlatma, saat/kamera, vinç/apartman veya video modellerine alternatif animasyon** hakkındaysa, ana kurgu sürecine başlamadan önce:

1. `integrations/blender-higgsfield/AGENTS.md`
2. `integrations/blender-higgsfield/AGENT-RUNBOOK.md`
3. `integrations/blender-higgsfield/docs/VIDEO-ENVANTER.md`
4. `integrations/blender-higgsfield/docs/ACCEPTANCE.md`

dosyalarını oku. Kurulum tespiti için **entegrasyon klasöründe** `python scripts/doctor.py --json` çalıştır. Offline tanılama MCP'nin gerçekten bağlı olduğunu **kanıtlamaz**; canlı bağlantıyı salt-okunur MCP çağrısıyla ayrıca doğrula. Bulut modelleri için OAuth ve hesap onayını kullanıcı tamamlar; tahmini kredi/maliyet ve izin olmadan ücretli üretime geçme. Önce küçük ücretsiz önizleme, sonra kullanıcı incelemesi, sonra final. Ana atölyenin mevcut iş güvenliği ve onay protokolü geçerli kalır.
