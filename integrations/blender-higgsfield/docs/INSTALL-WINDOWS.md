# Windows 10/11 kurulum — ajan için elle doğrulanabilir adımlar

Bu dosya **programları GitHub'a koymaz**; Windows bilgisayarına güvenilir dağıtım kanallarından kurmak için komutları ve testleri gösterir. İndirilen programların veya ücretli servislerin onayını kullanıcı vermelidir.

## 1. Önce kontrol et

PowerShell aç ve deponun `integrations/blender-higgsfield` klasörüne geç:

~~~powershell
python scripts/doctor.py --json
~~~

`MISSING` çıkan programları yeniden indirmeden önce Windows'taki mevcut kurulumları incele. Bu tanılama Blender'ın çalışmasını veya Higgsfield oturumunu doğrulamaz.

## 2. Eksikleri resmî dağıtımdan kur

Kurulu değilse **yalnız eksik olanı** kur; Windows'un paket yöneticisi onay isteyebilir.

~~~powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id BlenderFoundation.Blender -e
winget install --id astral-sh.uv -e
winget install --id Gyan.FFmpeg -e
~~~

Codex CLI için OpenAI'nin [resmî kurulum rehberi](https://github.com/openai/codex#installing-and-running-codex-cli) yolunu kullan. Node.js/npm zaten varsa:

~~~powershell
npm install -g @openai/codex
~~~

Node/npm yoksa Codex resmî dağıtımında Windows kurulumu da mevcut; internetten bilinmeyen PowerShell betiği çalıştırma. Resmî indirme: https://github.com/openai/codex/releases/latest

**Önemli:** Bu komutlar bilgisayarında sen/yerel ajan tarafından çalıştırılacaktır, GitHub CI çalıştırmaz. Program kurulumu için kullanıcı onayı alın.

## 3. Yeni PowerShell aç

~~~powershell
git --version
python --version
uv --version
codex --version
ffmpeg -version
blender --version
~~~

Blender Windows'ta yüklü olup `blender` PATH üzerinde bulunmayabilir. `C:\Program Files\Blender Foundation\` altındaki ilgili `blender.exe` dosyasının **gerçek** yolunu bul ve o tam yolu kullan. Resmî Lab MCP için Blender 5.1 veya daha yeni olmalı.

Codex hesabını çalıştırırken oturum aç: `codex`, ardından kullanıcı olarak OpenAI hesabınla giriş yap. Parola veya gizli anahtarı ajana verme.

## 4. MCP seçeneklerinden yalnız birini kur

Resmî (Blender Lab):

~~~powershell
.\scripts\install.ps1 -Backend official
~~~

Ardından Blender 5.1+ içinde https://www.blender.org/lab/mcp-server/ adresinde anlatılan Blender Lab MCP add-on yükleme/etkinleştirme adımlarını tamamla.

**Alternatif topluluk**: `.\scripts\install.ps1 -Backend community`; Blender'da `N → MCP for Blender` panelini kontrol et. İki backend aynı anda başlatılmamalı.

Kayıt kontrolü: `codex mcp list`. Gerçek canlı kontrol: Codex'e "Blender MCP ile açık sahnenin nesnelerini sadece listele, hiçbir şey değiştirme" de; sonuç gelirse bağlantı çalışıyor.

## 5. Ücretli servis isteğe bağlı

Higgsfield için `docs/HIGGSFIELD.md`. Kullanıcı hesabında OAuth olmadan bağlantı çalışmaz. Hiçbir video modelini otomatik çağırma; önce kullanıcının kredi ve maliyet onayını al.

## 6. Başarılı durum testi

~~~powershell
python -m unittest discover -s tests -v
python scripts/doctor.py --json
~~~

`tests` geçmesi Blender render yaptığını kanıtlamaz. Blender kuruluysa arka planda tek kare dene:

~~~powershell
blender --background --python blender/scenes/camera_exploded.py -- --render still --quality preview --output outputs
~~~

`outputs/camera_exploded_preview.png` görüntüsünü açıp incele. Kullanıcı izin vermeden 720 kare animasyon render'ını başlatma.

## Kaynaklar

- https://www.blender.org/download/
- https://www.blender.org/lab/mcp-server/
- https://docs.astral.sh/uv/getting-started/installation/
- https://github.com/openai/codex
- https://ffmpeg.org/download.html
