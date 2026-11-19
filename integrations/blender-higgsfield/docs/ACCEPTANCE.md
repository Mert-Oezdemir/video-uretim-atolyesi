# Kurulum ve render kabul kontrolleri

İlk aşamada hiçbir ödeme gerektirmemelidir. Gerçek makinede aşağıdaki sonuçları görmeden **tam kuruldu** deme.

## A. Otomatik / offline kontroller

`python scripts/doctor.py --json`: ihtiyaç duyulan CLI komutları için PASS/MISSING; kaynak klonlanmadıysa NOT_INSTALLED; eklenti/OAuth için NOT_VERIFIED.

`python -m unittest discover -s tests -v`: paket testleri yeşil. `bash -n scripts/install.sh`, `node --check` (web HTML içindeki betiği çıkararak) statik doğrulama.

Bu kontroller yalnızca kod yapısını doğrular.

## B. Kullanıcı bilgisayarında gerçek kontroller

- `blender --version`: resmî MCP kullanılacaksa 5.1+.
- `uv --version` ve `codex --version`.
- `codex mcp list`: *yalnız bir* aktif Blender tanımı; `mcp list` tek başına bağlantı testi değildir.
- Blender içinde resmî Lab MCP veya topluluk MCP add-on açık.
- Codex MCP çağrısından Blender sahnesinin salt-okunur nesne listesi gelir.
- Higgsfield yalnız kullanıcı isteğiyle eklenir; OAuth tamamlandıysa salt okunur hesap sorgusu yapılabilir. Bu hizmet opsiyoneldir.
- Arka planda `--render none` sonucu `outputs/camera_exploded.blend` gerçekten oluşur.
- `--render still` sonucu `outputs/camera_exploded_preview.png` gerçekten oluşur ve incelenir.
- Kullanıcı final render'a onay verdiyse `--render animation` sonucu MP4 üretilir, `ffprobe` ile süre, oran ve codec kontrol edilir.
- Tüm çıktılar `outputs/` altında kalır; hiçbir şifre, ödeme anahtarı veya özel dosya repoya commit edilmez.

## C. Bilinen sınırlamalar

- Blender'ı veya Higgsfield hesabını bir GitHub commit'i kuramaz/bağlayamaz.
- GitHub Actions ortamında Blender ve GPU render yoktur; CI başarıları yalnız testlerdir.
- Örnek 3D sahne **ticari seviyede kusursuz model vaat etmez**; geliştirilebilir starter'dır.
- HTML demo canlı canvas animasyonudur; MP4 export otomatik değildir.
- Kodun gerçek Blender 5.1+ sürümünde çalışması kullanıcı/ajan makinesinde doğrulanmalıdır.
- Geniş sahne, oyun, e-ticaret konfigüratörü, haber içerik üretimi için ayrı iş brief'i ve test gerekir.
