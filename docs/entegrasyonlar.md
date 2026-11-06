# İsteğe bağlı entegrasyonlar

Yerel komutlar video dosyalarıyla çalışır. Aşağıdaki uygulamaları, üretim biçimine göre giriş ve çıkış noktalarına bağlayabilirsin. Kayıt, bulut hesabı, görsel üretim, insan onayı ve yayın işlemleri ayrı adımlar olarak kalır.

## Kayıt ve ses

- **Cap Studio** ile pencereyi veya ekranı kaydet. Düzenlenebilir Cap projesini sakla ve yerel MP4 çıktısını işin `raw/` klasörüne kopyala. Ekran demosunda örnek veri kullan. Tıklama, bekleme ve sonuç ekranı izleyici için anlamlıysa o aralığı koru. [Cap Studio](https://cap.so/docs/recording/studio-mode) · [Cap ajan komutları](https://cap.so/docs/agents/workflows)
- **Playwright** ile aynı tarayıcı adımlarını yeniden kaydedebilirsin. Depodaki [tarayıcı demosu](../demo-browser/README.md) örnek veriyi yerel sayfada gösterir. Kayıt klibini kurguda kullan. Tıklama işaretleri, sahneye zoom ve ok eklemek için zaman kodu önerisi sağlar. Kaydı kestiğinde bu işaretleri onaylı kurguya yeniden eşle. [Playwright video kaydı](https://playwright.dev/docs/videos)
- **OBS** ayrı mikrofon ve uygulama sesi izleri gerektiğinde kullanılabilir. Diyalogdan transkript üretirken temiz mikrofon izini kullan. FFmpeg'in `sidechaincompress` filtresiyle konuşma sırasında müzik seviyesini azaltmayı deneyebilirsin. [OBS uygulama sesi](https://obsproject.com/kb/application-audio-capture-guide) · [FFmpeg ses filtresi](https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress)

## Yerel transkript ve altyazı

Windows'ta Whisper'ı Python ortamına kur. Uyumlu Python ve PyTorch sürümü için kendi belgelerini kontrol et. İlk model indirmesi ağ gerektirir. Daha küçük çok dilli bir modelle kısa bir pilot çalıştır. Mikrofon kalitesine ve donanıma göre model seçimini değiştir. [OpenAI Whisper kurulumu](https://github.com/openai/whisper#setup) · [PyTorch kurulumu](https://pytorch.org/get-started/locally/)

Apple Silicon Mac'te `mlx-whisper` paketi ile aynı iş klasörünü kullanabilirsin. `transcribe` komutuna `--backend mlx-whisper` ekle. Özel bir model için `--model` ile dönüştürülmüş modelin dizinini veya Hugging Face depo adını ver. [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper)

**Subtitle Edit** ile `transcript/final.srt` içindeki okuma hızı, uzun satır, çakışma ve süre sorunlarını listele. Ürün adlarını ve teknik terimleri düzelt. Düzeltilen altyazıyı önizleme ve final render için aynı dosya yolundan geçir. [Subtitle Edit hata listesi](https://subtitleedit.github.io/subtitleedit/features/list-errors.html)

## Ajan, kaynaklar ve medya arşivi

- Bir yönetici ajan seç. Codex veya Claude Code'dan zaman kodlu transkripti ve onaylı brief'i kullanarak aday kesim ve sahne planı oluşturmasını iste. Kaynak aralıklarını, grafik talimatını ve gereken dosyaları ayrı kaydet. Bir sahnenin süresi değişirse ona bağlı altyazı, grafik ve bölüm zamanlarını da gözden geçir. [Codex etkileşimsiz kullanım](https://developers.openai.com/codex/noninteractive) · [Claude Code etkileşimsiz kullanım](https://code.claude.com/docs/en/headless)
- **Avenox Beyin ve Obsidian Bases** ile `source_url`, `version`, `approved`, `aspect` ve `asset_path` gibi alanları olan yerel Markdown kayıtları tut. İş dosyalarındaki sahne veya kaynak kimliğini bu kayıtlara bağla. Büyük medyayı yerel iş diski üzerinde sakla. Yeni bir klip üretmeden önce onaylı sürümlere bak. [Avenox Beyin Windows](https://github.com/avenoxai/avenoxbeyin/blob/main/SETUP-WINDOWS.md) · [Obsidian Bases](https://obsidian.md/help/bases)
- Mimari şemalar için Mermaid'den SVG alabilirsin. Karşılaştırma sayıları, kod satırları ve kaynak etiketleri için doğruladığın verileri [HyperFrames şablonlarına](../graphics/README.md) gir. [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli)

## Topview klipleri

1. İhtiyacın olan sahneyi, süresini, oranını ve kabul ölçütünü yaz. Kullanım hakkına sahip olduğun referansları seç.
2. Codex veya Claude Code içinde Topview eklentisini resmi yönergeyle bağla ve OAuth oturumunu aç. Model seçimi ve tahmini maliyeti kontrol et. Üretim adımını kullanacağın taslağa göre çalıştır. [Topview Codex](https://github.com/topviewai/plugins/blob/main/docs/codex.md) · [Topview Claude Code](https://github.com/topviewai/plugins/blob/main/docs/claude.md)
3. Onaylı klibi indirip iş klasörünün `assets/` dizinine koy. Klibin modelini, sürümünü, üretim tarihini ve kullanım notunu medya kataloğuna yaz. Klibi zaman kodlu görüntü katmanı olarak kullan. Render bu katmanın görüntüsünü ve ana kurgunun sesini alır. Klip orijinal zaman çizelgesini uzatacaksa kesimi önce güncelle ve altyazıyı yeniden zamanla.

Seri üretim için API yolunu seçersen resmi belgelerdeki fiyat tahmini ve görev durumunu kullan. Görev kimliğini kaydedip yeniden denemeden önce mevcut görevin durumunu sorgula. Bu repo bulut hesabı açmaz, API anahtarı yönetmez ve Topview üretimini tetiklemez. [Topview API](https://platform.topview.ai/docs)

## Kısa form ve yayın

- **9:16** için onaylanmış uzun kurgudan kendi başına anlaşılır bir kesit veya yeni bir dikey kayıt seç. Dikey klibi ayrı iş klasöründe aç, dikey şablonu render et ve onun zamanına göre yeni SRT oluştur. Arayüzün önemli bölgelerini ve platform katmanlarıyla çakışabilecek altyazıyı telefonda kontrol et. Uygun kanalda Short'a uzun videoyu ilgili video olarak bağlayabilirsin. [YouTube ilgili video](https://support.google.com/youtube/answer/14075157?hl=tr)
- **İngilizce** için onaylı Türkçe SRT'nin zamanlarını koruyarak `transcript/final.en.srt` hazırla. Satırların okunurluğunu ve teknik terimleri ayrıca kontrol et. `package` bu dosyayı doğrulayıp `captions.en.srt` olarak ekler. Başlık ve açıklama çevirilerini Studio'da ekleyebilirsin. [YouTube yerelleştirme](https://support.google.com/youtube/answer/4792576?hl=tr)
- **Yayın incelemesi** sırasında ana MP4, altyazı, kapak, başlık, açıklama, bölüm zamanları ve kaynak listesini birlikte kontrol et. Video yüklendikten sonra Studio'daki izleyici tutma noktalarını sahne zamanlarıyla karşılaştır. Tek bir grafikten neden çıkarmak yerine sonraki videoda sınanabilir bir değişiklik seç. Uygun uzun videolarda başlık veya kapak varyantlarını Studio'da test edebilirsin. [İzleyici tutma](https://support.google.com/youtube/answer/9314415?hl=tr) · [Başlık ve kapak A/B testi](https://support.google.com/youtube/answer/16391400?hl=tr)

## Ek kalite kontrolleri

- Tesseract ile seçilmiş ekran karelerindeki yazıları ve koordinatları çıkarabilirsin. Adres, e-posta veya anahtar biçimine benzeyen metinleri inceleme adayı olarak işaretle. Hareketli ve küçük yazılarda örneklenmeyen kareler olabileceği için sansürü videoyu izleyerek doğrula. [Tesseract komut satırı](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage#tsv-output) · [Türkçe dil verisi](https://github.com/tesseract-ocr/tessdata/blob/main/tur.traineddata)
- Ekran demosundaki kasıtlı duraklamaları ve durağan bölümleri önizlemede kontrol et. Beklenmedik siyah kare veya donma adayları için FFmpeg'in `blackdetect` ve `freezedetect` filtrelerini kullanabilirsin. [FFmpeg filtreleri](https://ffmpeg.org/ffmpeg-filters.html)
- Revizyonu zaman kodu, sahne kimliği ve istenen değişiklikle kaydet. Yeni render'da düzeltilen aralığı ve komşu kesimleri tekrar izle.

## Ayrı kurgu rotası ve kaynaklar

**video-use** kendi kesim ve transkript akışına sahip bir seçenektir. Belgelenen kurulum, sesten transkript almak için ElevenLabs Scribe kullanır. Bu rotayı ayrı bir deneme işinde değerlendir. Yerel Whisper çıktısı için `video-use` zaman kodu sözleşmesine uygun bir dönüştürücü gerekir. [video-use](https://github.com/browser-use/video-use) · [Kurulum](https://github.com/browser-use/video-use/blob/main/install.md)

Bu atölyenin tasarımında açık kaynak [Avenox Studio](https://github.com/avenoxai/avenoxskills/tree/main/avenox-studio) ve [Sirio Berati'nin YouTube AI Video Editing System](https://github.com/sirioberati/YouTube-AI-Video-Editing-System) akışları referans alındı. Bu depoların kodu, video anlatımının transkripti ve üretim varlıkları paketin parçası değildir.
