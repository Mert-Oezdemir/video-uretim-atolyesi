# HyperFrames sahne şablonları

`build.py`, JSON sahne tarifinden yerel bir HyperFrames projesi oluşturur. [Önce/sonra](examples/before-after.json), [kod değişikliği](examples/code-diff.json), [mimari akış](examples/architecture.json) ve [kaynak kartı](examples/source-card.json) örnekleri doğrudan girdi olarak kullanılabilir.

Gerekenler Python 3.10+, Node.js 22+ ve PATH'te FFmpeg. Aşağıdaki komutlar Windows PowerShell'de repo kökünden çalışır. HyperFrames'in ilk kullanımı npm paketini ve gerekiyorsa bir tarayıcıyı indirir. Oluşturulan HTML dış web kaynağı çağırmaz.

```powershell
$scene = 'jobs/demo/graphics/kart'
python graphics/build.py graphics/examples/before-after.json $scene --aspect 16:9 --transparent
npx.cmd --yes hyperframes@0.9.19 check $scene --snapshots
$overlay = Join-Path (Get-Location).Path 'jobs/demo/graphics/kart.mov'
npx.cmd --yes hyperframes@0.9.19 render $scene --format mov --fps 30 --workers 1 --output $overlay
```

`--transparent`, panonun dışında alfa bırakır. MOV varsayılan olarak ProRes 4444 kullanır. Tek başına izlenebilen tam ekran sahne için `--transparent` bayrağını çıkar ve MP4'e render al. `--aspect 9:16` 1080 × 1920 pano oluşturur. Bu panoyu dikey bir ana video üzerinde kullan. `--accent '#bcf0bc'` vurgu rengini değiştirir. `--font .\marka.woff2` yerel fontu sahne klasörüne kopyalar. Varsayılanı Segoe UI ve Arial'dır.

İstersen `jobs/demo/graphics/overlays.json` içinde panonun onaylı videodaki yerini belirt. `duration`, JSON sahnesindeki süreyi aşmamalı. `start` kesimden sonraki video zamanıdır.

```json
{
  "overlays": [
    {"path": "graphics/kart.mov", "start": 1.0, "duration": 2.0}
  ]
}
```

```powershell
python -m atolye render jobs/demo --input cut/locked.mp4 --overlays graphics/overlays.json --captions transcript/final.srt --preview
```

Şablonlar kısa, sabit panolar üretir. `graphics/style.css` marka görünümünü düzenler. Uzun metin ve geniş kod satırları ekranda taşabileceği için `check --snapshots` çıktılarını incele. Hareket eklersen HyperFrames'in zaman çizelgesine bağlı, kareye göre ilerleyen animasyonları kullan. [HyperFrames CLI](https://github.com/heygen-com/hyperframes/blob/main/docs/packages/cli.mdx) · [HTML şeması](https://github.com/heygen-com/hyperframes/blob/main/docs/reference/html-schema.mdx)
