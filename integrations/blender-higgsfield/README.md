# Blender + Codex + Higgsfield — Video Üretim Kiti

Videodaki yaklaşımı mevcut Video Üretim Atölyesi deposuna ekleyen bağımsız bir modül.

**İçerik:** Resmî Blender Lab MCP veya topluluk MCP kurulumu, Codex yapılandırması, Python ile koddan 30 saniyelik dikey 3D ürün animasyonu, HTML/Canvas animasyon demosu, Higgsfield bağlantı rehberi.

**Sınır:** Blender/MCP/Codex yerelde kurulur. Higgsfield, Seedance, Kling, Nano Banana ve ElevenLabs bulut hizmetleridir; GitHub'a indirilemez. Bağlantı hesabının yetkilendirilmesi ve kredileri ayrı gereklidir.

## Ajan / Codex için ilk okuma (önemli)

Bu depoyu bir ajana verirsen göreve **önce** şu dosyalardan başlamasını söyle:

1. `../../AGENTS.md` (ana atölye kuralları)
2. `AGENTS.md` (entegrasyonun güvenlik kuralları)
3. `AGENT-RUNBOOK.md` (hangi görevde hangi aracı nasıl denetleyeceği)
4. `docs/VIDEO-ENVANTER.md` (videodaki araçların hangisi hazır, hangisi fikir)
5. `docs/ACCEPTANCE.md` (kurulu/çalışır demek için gerekli kanıtlar)

Kurulumun gerçekten yapılıp yapılmadığını önce şu komutla kontrol et:

~~~bash
python scripts/doctor.py --json
~~~

**Bunlar önemli farklardır:** Ajanın gördüğü GitHub dosyaları ≠ bilgisayardaki uygulama kurulumu. `codex mcp list` kaydı ≠ çalışır Blender bağlantısı. Statik CI testi ≠ gerçek Blender render'ı. Kredi harcamayan kurulum betiği ≠ Higgsfield hesabının bağlanması.

Bir ajana verilebilecek başlangıç görevi:

> AGENTS.md ve AGENT-RUNBOOK.md dosyalarını oku, doctor raporu üret, resmî Blender MCP'nin gerçekten çalışıp çalışmadığını salt-okunur bağlantı testiyle kontrol et. Sorun varsa hangi adımın kullanıcıdan beklendiğini açıkça yaz. Ücretli üretim yapmadan önce ücretsiz tek kare önizleme göster.

## Gereksinimler

- [Blender 5.1 veya üzeri](https://www.blender.org/download/) (resmî MCP için)
- [Git](https://git-scm.com/downloads)
- [uv ve uvx](https://docs.astral.sh/uv/getting-started/installation/)
- [Codex CLI](https://developers.openai.com/codex/cli) (MCP kullanımı için)
- [Windows ayrıntılı kurulum ve kontrol rehberi](docs/INSTALL-WINDOWS.md)

Windows'ta uv: `winget install --id=astral-sh.uv -e`. Kurulumdan sonra yeni terminal aç.

## Yerel bağlantıyı kur

~~~powershell
git clone https://github.com/Mert-Oezdemir/video-uretim-atolyesi.git
cd video-uretim-atolyesi/integrations/blender-higgsfield
.\scripts\install.ps1 -Backend official
~~~

macOS/Linux:

~~~bash
git clone https://github.com/Mert-Oezdemir/video-uretim-atolyesi.git
cd video-uretim-atolyesi/integrations/blender-higgsfield
bash scripts/install.sh official
~~~

Bu kurulum resmî Blender MCP kaynaklarını `vendor/blender_mcp` içine Git ile getirir; Codex CLI kuruluysa `blender` MCP kaydını oluşturur. Blender uygulamasını veya Blender içindeki resmî eklentiyi kendi kendine kurmaz.

**Blender içindeki son adım:** Edit → Preferences → Get Extensions menüsünden [Blender Lab](https://lab.blender.org/) deposunu etkinleştir, MCP eklentisini kur/aç. Resmî rehber: https://www.blender.org/lab/mcp-server/

Alternatif, topluluk eklentisini kullanmak için: `.\scripts\install.ps1 -Backend community` veya `bash scripts/install.sh community`. Bu seçenek `uvx mcp-for-blender install-addon` çalıştırır. Aynı anda iki Blender MCP sunucusunu açma. Var olan Codex `blender` girişi güvenlik için üzerine yazılmaz; değiştirmek için önce `codex mcp remove blender`.

## Blender ile örnek animasyonu üret

Bu örnek haricî görsel gerektirmeyen **30 saniye, 24 fps, 9:16** ürün-patlatma animasyonudur.

Önizleme tek karesi:

~~~bash
blender --background --python blender/scenes/camera_exploded.py -- --render still --quality preview --output outputs
~~~

MP4 animasyon:

~~~bash
blender --background --python blender/scenes/camera_exploded.py -- --render animation --quality preview --output outputs
~~~

Yüksek çözünürlüklü render için `--quality final` kullan. Betik ayrıca `outputs/camera_exploded.blend` kaydeder. Komutları bu modül klasörünün içinden çalıştır. Blender'ın sistem PATH'inde bulunmaması durumunda Blender yürütülebilir dosyasının tam yolunu gir.

## Sadece kodla animasyon

`web/index.html` dosyasını tarayıcıda aç. Vinçle katların üst üste dizildiği, kamera ve toz efektli saf HTML/Canvas örneği için Blender veya internet gerekmez.

## Higgsfield / Seedance / Kling

[Higgsfield rehberi](docs/HIGGSFIELD.md) hesap yetkilendirmesini ve istenirse Codex'te uzak MCP bağlantısını anlatır. **Kurulumun kendisi hiçbir Higgsfield kredisi harcamaz.** Ücretli her üretim için önceden açık onay iste.

## Güvenlik

Blender'ın [resmî MCP açıklaması](https://www.blender.org/lab/mcp-server/) AI tarafından oluşturulan Python'un dosyalara erişebileceği uyarısını yapar. Güvenmediğin betikleri çalıştırma; ayrı kullanıcı profili veya sanal makine kullan. Haricî kaynakları bu depoya lisanssız kopyalamıyoruz; kendi kaynaklarından çekiyoruz. Mevcut ana video atölyesi akışı değiştirilmedi.

Kaynaklar: [resmî Blender MCP](https://projects.blender.org/lab/blender_mcp/wiki/Setup) · [topluluk MCP](https://github.com/ahujasid/mcp-for-blender) · [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp) · [Higgsfield MCP](https://higgsfield.ai/mcp).
