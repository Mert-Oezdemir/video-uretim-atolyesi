# Tekrar çekilebilir tarayıcı demosu

Playwright, paketteki kurgusal arayüzü açar ve iki eylemi sabit boyutlu bir tarayıcıda kaydeder. Demo sayfası tamamen yereldir. Chrome ve bağımlılıklar hazır olduğunda dış web sitesi veya hesap kullanmaz.

Windows PowerShell, repo kökü ve Node.js 22+:

```powershell
Push-Location demo-browser
npm.cmd ci
npx.cmd playwright install --only-shell chromium
Pop-Location
node demo-browser/capture.mjs jobs/demo/raw/browser
```

Çıktılar `demo.webm` (1280 × 720, sessiz) ve `markers.json`. İşaretler tıklamanın yaklaşık saniyesi, etiketi ve hedefinin merkezini taşır. Yeri ve zamanı önizlemede doğrulayıp sahne planına aktar. Tekrar kayıt için yeni bir çıktı klasörü kullan.

Bu klibi sessiz ara görüntü olarak ya da ayrı kaydedilmiş anlatımın altında kullanabilirsin. Tarayıcı akışını gerçek bir ürüne uyarlarken örnek veri ve bir test hesabıyla kaydet. [Playwright video kaydı](https://playwright.dev/docs/videos) · [Örnek veri kullanımı](https://playwright.dev/docs/mock)
