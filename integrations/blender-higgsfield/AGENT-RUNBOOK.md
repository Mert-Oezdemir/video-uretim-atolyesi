# Ajan çalışma kitabı — Blender, Codex ve Higgsfield

Bu dosya bir çalıştırma sözleşmesidir. Önce depo kökündeki `AGENTS.md`, ardından bu klasördeki `AGENTS.md` ve bu dosyayı oku.

## 1. Gerçek kurulum durumu

- Depodaki Python/HTML kodlarının varlığı, Blender, Blender MCP, Codex veya Higgsfield'ın kullanıcı bilgisayarında kurulu olduğu anlamına **GELMEZ**.
- Başlangıçta `python scripts/doctor.py --json` çalıştır ve JSON sonucunu incele. Bu tanılama sadece ortam/CLI/yerel kaynak varlığını ölçer; **canlı MCP bağlantısını, Blender add-on durumunu, OAuth yetkisini veya krediyi doğrulayamaz**.
- Yerel programların yokluğunda kullanıcıya doğru kurulum adımını göster; kurulmadıysa "kuruldu" deme.
- `codex mcp list` MCP **tanımlarını** gösterebilir ama sunucunun açık ve bağlı olduğunu tek başına kanıtlamaz.
- Gerçek bağlantıyı MCP araçlarıyla salt okunur bir sorguyla kontrol et: sahne objelerini *listele*, hiç kod yürütme. MCP istemcinde araç görünmüyorsa `NOT_VERIFIED` raporla.
- Higgsfield bağlantısını kullanıcı yetkilendirir. Hesap bakiyesi/araç listesi okunabiliyorsa salt okunur kontrol et; **üretim çağrısı yapma**.

## 2. Belirleyici durum makinesi

Her adım için `PASS`, `FAIL`, `BLOCKED`, `NOT_VERIFIED` değerlerinden birini kullan:

| Adım | Başarı ölçütü | Başarı olmasa ne yap |
|---|---|---|
| PRECHECK | `doctor.py` CLI ve araçları raporladı | Eksik programın resmî kurulum bağlantısını ver |
| MCP_CONFIG | İstenen tek Blender backend Codex'e tanımlandı | Mevcut kaydı sessizce değiştirme |
| MCP_LIVE | Açık Blender'dan salt okunur sahne bilgisi döndü | Kullanıcıdan Blender + eklentiyi açmasını iste |
| HIGGSFIELD_AUTH | Hesaptan salt okunur bağlantı cevabı alındı | Kullanıcı girişi/OAuth bağlantısı bekle |
| SOURCE_OK | Sadece güvenilir ve lisanslı kaynaklar kullanıldı | İndir/kur çalıştırma |
| BLEND_BUILD | Blender arka plan komutu 0 koduyla çıktı, .blend oluştu | Hata günlüğünü ilet |
| STILL_RENDER | PNG oluştu, çözünürlük/boyut doğrulandı | Final videoya geçme |
| REVIEW | Kullanıcı gerekli görsel onayı verdi | Render/üretim başlamasın |
| VIDEO_RENDER | MP4 gerçekten var, süre ve fps kontrol edildi | "hazır" deme |
| PUBLISH | Kullanıcı açıkça yayınlama talimatı verdi | Otomatik yayınlama yapma |

`doctor.py` PASS vermesi MCP_LIVE demek değildir.

## 3. Göreve göre doğru motor

| Görev | Öncelikli yöntem | Ne zaman ücretli modele geç |
|---|---|---|
| Kat kat inşa edilen bina, hareketli grafik | `web/index.html` şablonunu geliştir, HTML/Canvas/JS | Gerçek çekim gibi dokulu sıra dışı görüntü gerekiyorsa |
| Saat/kamera ürün exploded-view, minyatür köy, tren | Blender + Python + Cycles | Fotogerçek referans materyali gerekiyorsa |
| Oyuncunun kontrol ettiği dünya | Ayrı oyun motoru/web uygulaması; bu starter **oyun motoru kurmaz** | Görsel referans/asset gerekiyorsa |
| Ev/koltuk/mutfak seçimi veya bilet koltuğu görünümü | Ayrı web uygulaması, ürün/veri modeli gerekir | Satış görselleri referans gerektiriyorsa |
| Ses, müzik, ses efektleri | Mevcut medya/FFmpeg iş akışı | Lisanslı/hesaplı ses modeline onay verildiyse |
| Gerçek olaya dayalı canlandırma | Kaynakları doğrula; **temsili canlandırma** etiketle | Kaynak, hak ve maliyet onayı varsa |

Bu tablodaki örnek fikirlerin hepsi hazır uygulamalar değildir. Yalnızca örnek kamera 3D sahnesi ve örnek bina Canvas sahnesi çalıştırılabilir başlangıç kodu olarak depodadır.

## 4. Üretim protokolü

1. **Amaç:** Kullanıcının istediği sahne türü, çıktı (9:16/16:9), süre, hedef çözünürlük ve teslim klasörü. Bilgi eksikse makul varsayımı açıkça belirt.
2. **Kapasite keşfi:** `python scripts/doctor.py --json`. Çalışmayan araçları listele; tek backend seç. Ücretli bağlayıcıları otomatik başlatma.
3. **Plan:** Saat/sahne, kamera, ışık, obje, varlık hakları, render motoru, tahmini bellek/süre. Önce ücretsiz kod seçeneğini değerlendir.
4. **Çalışma alanı:** Sadece kullanıcının belirlediği iş klasörü. Kaynak/ham medya korunsun. Hassas dosyaları, anahtarları, müşteri verilerini Git'e atma.
5. **Hazırlık:** Yerelde `blender --background --python blender/scenes/camera_exploded.py -- --render none --quality preview --output outputs` ile .blend oluşturmayı dene. Bu komut mevcut Blender sahnesini sıfırlar; **arka planda boş Blender oturumunda** çalıştır, kullanıcının açık projesine uygulama.
6. **Önizleme:** Ayrı arka plan Blender işleminde `--render still` çalıştır ve PNG'yi incele. Render hatasından sonra final video başlatma.
7. **Onay:** Kritik değişikliklerde kullanıcıdan onay al. GPU/render süresi yüksek veya ücretli bulut işlemleri için özellikle maliyet/limitleri belirt.
8. **Final:** Onay varsa `--render animation`. MP4'ü `ffprobe` ile süre, çözünürlük, fps açısından doğrula. Varsa ana atölyeye `jobs/...` girdisi olarak aktar; ana projenin `README.md` önizleme/final prosedürünü uygula.
9. **Teslim:** Gerçek dosya yolları, kullanılan araçlar, sürümler, kalan bloklar, üretimde harcanan kredileri belirt. Sorunları gizleme.

## 5. Açık yasaklar

- Sırf ajan istek yazdı diye Blender MCP'ye güvenilmeyen Python kodu gönderme; MCP'nin Blender Python yürütme yetkisi geniştir.
- `vendor`/haricî kodu otomatik güncelleme, şüpheli kaynaktan kurma veya rastgele binary çalıştırma.
- `main` dalını, önceki işi, kaydı veya hazır çıktıları kullanıcı istemeden silme/üzerine yazma.
- Kullanıcı onayı olmadan Higgsfield/Seedance/Kling/Nano Banana/ElevenLabs üretimi başlatma, ücretli model seçme veya medya yükleme.
- Üretilmiş gerçekçi haber canlandırmasını gerçek çekim gibi sunma; yayın öncesi uygun AI açıklamasını kontrol et.
- Uygulama/eklenti kurulumu veya OAuth kullanıcı tarafından tamamlanmadıysa gerçek bağlantı varmış gibi davranma.

## 6. Agent komut şablonu

Kullanıcı "videodaki gibi yap" dediğinde:

`Bu repodaki AGENTS.md ve integrations/blender-higgsfield/{AGENTS.md,AGENT-RUNBOOK.md,docs/VIDEO-ENVANTER.md} dosyalarını oku. Önce doctor çalıştır, eksikleri ve gerçekten çalışan araçları raporla. Hiçbir ücretli servis isteği veya tam render yapmadan önce ücretsiz ve denetlenebilir önizleme öner. Mevcut Video Üretim Atölyesi onay protokolünü koru.`
