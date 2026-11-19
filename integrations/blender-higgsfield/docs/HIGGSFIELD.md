# Higgsfield bağlantısı

Videodaki Higgsfield **bulut hizmetidir**, GitHub içine yüklenemez. Hesabınla yetkilendirme ve abonelik gerekir.

## ChatGPT

1. https://higgsfield.ai/mcp → **Add Higgsfield to ChatGPT**.
2. ChatGPT → Plugins → Higgsfield → Add, ardından kendi hesabında oturum aç.
3. Bağlantı testi: "Higgsfield kredi bakiyemi göster." Bu işlem üretim oluşturmaz.

Resmî rehber: https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-ai-agent

## Codex / uzak MCP (isteğe bağlı)

MCP uyumlu Codex sürümünde:

~~~bash
codex mcp add higgsfield --url https://mcp.higgsfield.ai/mcp
codex mcp login higgsfield
codex mcp list
~~~

Bu üç komut otomatik kurulumda çalışmaz; hesap yetkisini sen verirsin. ChatGPT için doğrudan resmî Higgsfield eklentisini kullan.

## Kredi koruma

Önce Blender veya HTML koduyla üretilebilecek kısmı oluştur. Higgsfield ile üretime yalnızca ihtiyaç duyulan yerde geç. Ücretli her adımdan önce model, kredi maliyeti, ücretsiz alternatif ve açık onay iste. Bu bir talimattır, sistemsel harcama limiti değildir.

## Videoda anılan araçlar

| Ad | Kategori | Bu depodaki kapsam |
|---|---|---|
| Blender / Cycles / Python | Yerel | Python sahnesi, yerel render |
| Blender MCP resmî | Yerel MCP | Kaynak klonlama + Codex bağlantısı |
| mcp-for-blender topluluk | Yerel MCP | Alternatif kurulum |
| Codex / ChatGPT | Ajan | Bağlantı rehberi, kullanıcı girişi |
| Higgsfield MCP | Bulut | Eklenti / OAuth talimatları |
| Seedance, Kling, Nano Banana | Ücretli bulut modelleri | Ayrı kurulum yok; Higgsfield üzerinden isteğe bağlı |
| ElevenLabs / ses efektleri | Bulut ses üretimi | Otomatik çağrı yok |
| HTML/CSS/Canvas | Yerel web | web/index.html demo |
| Oyun / emlak / ürün konfigüratörleri | Uygulama örnekleri | Bu starter kapsamında ayrıca geliştirilmedi |

Video içeriklerinde gerçekçi olay canlandırmalarını **yapay canlandırma** olarak etiketle.
