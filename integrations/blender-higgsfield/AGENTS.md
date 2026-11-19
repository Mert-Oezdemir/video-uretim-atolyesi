# Blender–Higgsfield entegrasyonunda çalışan ajan

## Giriş noktası

Bu dizindeki görevler için önce `AGENT-RUNBOOK.md`, `docs/VIDEO-ENVANTER.md` ve `docs/ACCEPTANCE.md` oku. Ana deponun `../../AGENTS.md` kuralları da geçerlidir.

**Önce ortam durumunu kanıtla.** Burada betik bulunması, Blender/MCP/Codex/Higgsfield'ın kurulu veya bağlı olduğu anlamına gelmez. `python scripts/doctor.py --json` ile salt-okunur ön kontrol yap. Canlı Blender MCP bağlantısını ayrı bir salt-okunur nesne sorgusuyla doğrula; bu mümkün değilse `NOT_VERIFIED` yaz.

## Güvenli yürütme sınırları

- **Üçüncü taraf kaynak:** Blender Lab resmî: `https://projects.blender.org/lab/blender_mcp`; topluluk: `https://github.com/ahujasid/mcp-for-blender`. Bu iki backend alternatiftir; yalnız birini yapılandır.
- **Kod yürütme:** Blender MCP, Blender'da güvenilmeyen Python kodunu sınırlamadan çalıştırabilir. Sadece belirlenmiş iş klasörü; önceden görünür işlem planı; şüpheli betiği çalıştırma.
- **Ücretli servis:** Higgsfield/Seedance/Kling/Nano Banana/ElevenLabs OAuth/hesap gerektirir. Kullanıcının açık onayı olmadan üretim/medya yükleme/kredi harcama yok.
- **Çıktı:** Düşük çözünürlüklü still render → kullanıcı incelemesi → final video. Gerçek render dosyasını ve `ffprobe` verisini görmeden "hazır" deme.
- **İçerik:** Temsili haber veya gerçek dünyadaki olay görüntüsünü açıkça "Yapay canlandırma" olarak tanımla; kaynakları kendin doğrula, otomatik doğru sayma.
- **Dosyalar:** Ham kayıtları ve ana atölyenin kilitli kesimini değiştirme; onaylı çıktıyı silme; şifre, anahtar veya özel dosyaları commit etme.
- **Rapor:** Hangi adımlar `PASS`, `FAIL`, `BLOCKED`, `NOT_VERIFIED` açıkça göster. Eksik eklentiyi/oturumu kullanıcıya bildir.

Yalnızca mevcut dosyalarla hemen denenecek örnekler: `web/index.html` ve `blender/scenes/camera_exploded.py`. Videodaki oyun, emlak sitesi, bilet seçimi gibi örnekler henüz çalışır ürün olarak kurulmuş değildir.
