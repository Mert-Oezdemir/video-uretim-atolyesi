# Yerel üretim doğrulaması

7 Kasım 2026 tarihinde Windows üzerinde doğrulandı. Kapsam yerel üretim ve tek ajanla yönetimdir.

- Yedi otomatik test geçti. İlk altı test temiz bir kaynak kopyasında da geçti. Eklenen yedinci test, üç saniyelik görüntü ve bir saniyelik ses içeren gerçek bir MP4'ün reddedildiğini sınar. Sentetik videonun kesimi, ses ve görüntü süreleri, altyazı sınırları, Türkçe dosya yolları, dikey anlatım tabanı, Auto-Editor ve altyazı dil etiketi denetlendi.
- FFmpeg 9.0.2 ile H.264/AAC çıktı, ayrı SRT, altyazının görüntüye işlenmesi ve şeffaf ProRes katmanı doğrulandı.
- Auto-Editor 31.8.0, altı saniyelik kayıttan sessizliği çıkarıp yaklaşık 4,58 saniyelik video üretti.
- openai-whisper 20250625 ve PyTorch 2.14.1 CPU ile yerel transkript üretildi. Whisper small, Google FLEURS Türkçe geliştirme kümesindeki 3453892295047654520.wav kaydını çözdü. Metin referansla karşılaştırıldı ve sayı yazımı dışında aynı cümle elde edildi. Bu tek örnek bir genel doğruluk ölçümü oluşturmaz.
- Codex CLI ve Claude Code ile gerçek kesim ve sahne planları üretildi. Claude Code'un kayıtlı oturumu kullanmasını engelleyen bare modu kaldırıldı. Üretilen JSON planları yerel doğrulamadan geçti.
- Ajanın önerdiği kaynak aralıkları run komutuna verildi. Kesim, final transkripti, altyazılı dikey MP4 ve İngilizce etiketli yayın paketi tek çağrıda üretildi.
- HyperFrames 0.9.19 ile şeffaf MOV, Playwright 1.65.0 ile yerel tarayıcı kaydı doğrulandı.
- Eksik Whisper kurulumu kesim başlamadan reddedildi. Önizlemesiz final çağrısı reddedildi. Önizlemeden sonra kesim planının veya altyazının değişmesi, dosya özetleriyle yakalandı. Aynı işe ikinci üretimin girmesi kilitle engellendi.
- Türkçe ses kaydından yatay taban, small transkripti, altyazılı önizleme ve final yayın paketi üretildi. Final aşaması kilitli kesimi ve altyazıyı yeniden kullandı. MP4 karesi gözle incelendi ve Türkçe karakterlerin doğru çizildiği görüldü.
- verify, ses ve görüntünün süre veya başlangıç farkı 250 milisaniyeyi aşarsa hata verir. Bu kontrol kesim, render ve paketleme sırasında da uygulanır. Türkçe final dosyası bu kontrolü geçti. Konuşmanın dudak hareketiyle veya sahne anlamıyla eşleşmesi önizlemede değerlendirilir.

Türkçe ses kaynağı [Google FLEURS](https://huggingface.co/datasets/google/fleurs/tree/main/data/tr_tr). Test kayıtları, model dosyaları ve hesap bilgileri depoya eklenmez. Özel isimleri, teknik terimleri, kesimi ve görsel okunurluğu üretimde gözden geçir.

Yerel kontrolleri yeniden çalıştırmak için FFmpeg ve ffprobe'u PATH'e ekleyip depo kökünde `python -m unittest discover -s tests -v` çalıştır. Auto-Editor kuruluysa ilgili test de yürütülür. Gerçek konuşma çözümü için Whisper ortamı gerekir. Ajan bağlantılarında seçilen CLI hesabının oturumu açık olmalıdır.
