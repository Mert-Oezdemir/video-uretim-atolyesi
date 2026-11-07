# Kabul ölçütleri

Kapsam Windows üzerinde yerel üretim ve Codex veya Claude Code ile yönetimdir.

1. Temiz bir kopyada Python komutları ve sentetik demo çalışır.
2. Gerekli araç ve transkripsiyon bağımlılığı eksikse üretim başlamadan anlaşılır hata verilir.
3. Ham dosyalar korunur. Hatalı kesim ve iş dışına çıkan yollar reddedilir.
4. Yalnız ses, ekran ve ayrı anlatım girişleri yatay veya dikey tabana dönüşür.
5. Türkçe konuşmadan zaman kodlu JSON ve SRT üretilir.
6. İki ajan bağlantısı da kesim ve sahne planı üretir.
7. Önizlemenin girdileri değişirse final üretimi yeni önizleme ister.
8. Final üretimi onaylanan önizlemenin kilitli kesim ve altyazısını kullanır.
9. Yayın paketi gerçek MP4, doğru dil etiketi, kaynak listesi ve doğrulama raporu içerir.
10. İlgili otomatik testler ve gerçek medya denemeleri geçer. GitHub kaynakları ile yayınlanan sürüm aynı commit'e işaret eder.

Konuşma tanıma sonuçları ve sanatsal kararlar önizlemede değerlendirilir. Bu ölçütler bir konuşma modeline bütün kayıtlarda kusursuz yazım garantisi yüklemez.

Üretim, hata durumları ve temiz kaynak kopyası denemelerinin sonuçları [doğrulama kaydında](dogrulama.md) tutulur. Önizleme girdilerinin ve üretilen dosyaların özetleri iş klasöründe outputs/workflow-preview.json içinde saklanır.
