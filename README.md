# QueryRunner API

QueryRunner API, SQL Server üzerinde güvenli, denetlenebilir ve kontrollü SQL çalıştırmak için geliştirilmiş FastAPI tabanlı bir servistir.

API;

- JWT tabanlı authentication

- Kayıtlı (ön tanımlı) SQL çalıştırma

- Tarih aralığına göre otomatik SQL güncelleme

- Güvenli Raw SQL (SELECT / WITH / EXEC)

- MailLogger ile e-mail tabanlı audit log
  özelliklerini destekler.

⚠️ Güvenlik Notu
INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, MERGE gibi DDL/DML komutları otomatik engellenir ve tüm denemeler MailLogger üzerinden loglanır.

---

## 🚀 Versiyon

**v2.2.0 (Güncel Sürüm)**

- **v1.0.0** → Statik SQL sorguları
- **v2.0.0** → Dinamik tarih aralıklı SQL sorguları
- **v2.1.0** → `/query/v2/run-basic` (tarihsiz, statik sorgular)
- **v2.2.0** →
  - `/run-sql` → `note` alanı eklendi
  - Gelişmiş Raw SQL güvenliği (SELECT + WITH +EXEC dışı bloklama)
  - MailLogger (SMTP log gönderimi)
  - Genel API stabilite iyileştirmeleri

---

## Özellikler

- JWT tabanlı kullanıcı doğrulama
- Kayıtlı SQL sorgularını `items` veya `key` ile çalıştırma
- Tarih aralığı destekli sorgular (örnek: `"02.01.2025 ile 31.08.2025"`)
- Tarihsiz statik sorgular
- Güvenli Raw SQL (SELECT / WITH / EXEC)
- Raw SQL isteklerine opsiyonel `note` alanı (log amaçlı)
- Çoklu SQL çalıştırma (analiz senaryoları)
- MailLogger ile mail tabanlı log gönderimi
- Sağlık kontrolü endpointi (`/`)
- Docker ile containerize deploy desteği

---

## Kurulum

1. **Depoyu klonlayın:**

   ```sh
   git clone https://github.com/yourusername/QueryRunner-API.git
   cd QueryRunner-API
   ```

2. **Gerekli paketleri yükleyin:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Ortam değişkenlerini ayarlayın:**
   Proje kök dizininde `.env` dosyası oluşturun ve aşağıdaki örneğe göre doldurun:

   ```
    DB_SERVER=your_db_server_address
    DB_DATABASE_1=your_first_database
    DB_DATABASE_2=your_second_database
    DB_USER=your_db_username
    DB_PASSWORD=your_db_password
    # MailLogger için mail listesi

   MAIL_RECIPIENTS=example@gmail.com

   ```

4. **Veri Tabanı tablolarını hazırlayın:**

   ## Database schema

   database.py dosyasındaki get_user_by_username() fonksiyonu için kullanılacak Authentication tablosu (kullanıcı doğrulama için):

   ```sql
   CREATE TABLE [AUTHENTICATION TABLE](
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [kullanici] NVARCHAR(50) NOT NULL,
      [sifre] NVARCHAR(255) NOT NULL
   );
   ```

   database.py dosyasındaki get_sql_from_table2() fonksiyonu için kullanılacak Query tablosu (key, prompt ve sql saklanır):

   ```sql
   CREATE TABLE [db1].[dbo].[Query Table] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [key_] NVARCHAR(100) NOT NULL,
      [prompt] NVARCHAR(MAX) NULL,
      [query] NVARCHAR(MAX) NOT NULL
   );
   ```

## Çalıştırma

Uygulamayı başlatmak için:

```sh
uvicorn main:app --reload
```

API varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır.

## API Endpointleri

- `GET /` : Sağlık kontrolü sağlar.Sunucunun çalıştığını doğrulamak için kullanılır.
- `POST /auth/login` : Kullanıcı girişi yapar ve JWT token döner.
  Body örneği:

{
"username": "your_user_name",
"password": "your_password"
}

Yanıt:

{
"access_token": "<token>",
"token_type": "bearer"
}

- `POST /query/` : Veritabanında kayıtlı SQL sorgularını çalıştırır.İsteğe bağlı olarak tarih aralığı gönderilebilir.

## Body örneği (tarihli):

{
"items": ["Net_Satışlar"],
"Tarih": "02.01.2025 ile 31.08.2025"
}

## Body örneği (tarihsiz):

{
"items": ["Dönen_Varlıklar"]
}

- `POST /query/v2/run-basic`

Kullanıcıdan tarih bilgisi almadan statik SQL sorgularını çalıştırır (örneğin İK raporları gibi).

## Body örneği:

{
"key": "IK_Aylik_Ozet"
}

## Yanıt:

{
"user_id": 12,
"key": "IK_Aylik_Ozet",
"rowcount": 24,
"data": [...]
}

- `POST /query/raw/run-sql`

Sadece SELECT ve WITH ifadelerine izin verilir.
Tüm mutating SQL komutları otomatik olarak engellenir.
Bu endpoint artık tek SQL veya çoklu SQL listesi çalıştırabilir.

Desteklenen:
✔ SELECT
✔ WITH
✔ EXEC

Bloklanan:

❌ INSERT, UPDATE, DELETE
❌ DROP, ALTER, TRUNCATE
❌ CREATE
❌ MERGE
❌ SELECT dışı tüm komutlar

## Body örneği:

## Tek SQL Örneği

{
"sql": "SELECT _ FROM [Table Name] _;",
"note": "İK raporu için test sorgusu" #note alanı sadece loglama içindir.
}

## Çoklu SQL Örneği

{
"sql": [
"SELECT TOP 5 z_hat_kodu, COUNT(*) AS ArizaSayisi FROM db1.dbo.tabl1 GROUP BY z_hat_kodu",
"SELECT COUNT(*) AS ToplamAriza FROM db1.dbo.abc_table2"
],
"note": "Toplu analiz sorguları"
}

## Yanıt:Tek SQL de olsa çoklu SQL de olsa yanıt her zaman results listesi döner

✔ Tek SQL Yanıtı
{
"user_id": 12,
"results": [
{
"columns": ["col1", "col2"],
"rowcount": 10,
"rows": [
{ "col1": "A", "col2": 1 },
{ "col1": "B", "col2": 2 }
]
}
]
}
✔ Çoklu SQL Yanıtı
{
"user_id": 12,
"results": [
{
"index": 0,
"columns": ["z_hat_kodu", "ArizaSayisi"],
"rowcount": 5,
"rows": [ ... ]
},
{
"index": 1,
"columns": ["ToplamAriza"],
"rowcount": 1,
"rows": [ ... ]
}
]
}

- `POST /query/query` :

Kayıtlı SQL sorgularını çalıştırır. İsteğe bağlı tarih aralığı kabul eder.Bu endpoint, sistemde önceden tanımlı ve güvenli kabul edilen SQL sorgularını çalıştırmak için tasarlanmıştır.Kullanıcı SQL göndermez; yalnızca çalıştırılmasını istediği finansal / operasyonel kalemleri (items) belirtir.

## Kısa Çalışma Prensibi

- JWT token doğrulanır.
  items listesinde yer alan her kalem için:
- Backend’de tanımlı SQL bulunur.
  Tarih alanı gönderilmişse:
- SQL içindeki sabit tarih ifadeleri otomatik güncellenir.SQL’ler güvenli şekilde çalıştırılır.
- Her kalem için tek bir sonuç üretilir.
- Hata olan kalemler null döner, diğerleri çalışmaya devam eder.

## Header

- Authorization: Bearer <JWT_TOKEN>
- Content-Type: application/json

## Body

Tarihli Kullanım {
"items": [
"Net_Satışlar",
"Brut_Kar_Marjı"
],
"Tarih": "02.01.2025 ile 30.09.2025"
}

Tarihsiz Kullanım {
"items": [
"Dönen_Varlıklar",
"Toplam_Varlıklar"
]
}

## Result (Response)

{
"user_id": 3,
"items": [
"Net_Satışlar",
"Brut_Kar_Marjı"
],
"result": {
"Net_Satışlar": 4367646463635335.62,
"Brut_Kar_Marjı": 0.45345312
}
}

- `POST /query/query_automatized`

Bu endpoint, tarih bilgisi kullanıcıdan alınmadan, sistem tarafından otomatik hesaplanan tarih aralığı ile kayıtlı SQL sorgularını çalıştırmak için tasarlanmıştır.

Özellikle:

- Zamanlanmış işler
- Otomatik rapor mailleri
- LLM agent tetiklemeleri için kullanılır.

## Otomatik Tarih Hesaplama Mantığı

Bitiş Tarihi : Endpoint’in çağrıldığı gün (bugün)
Başlangıç Tarihi

- Eğer yıl 2025 ise → 02.01.2025
- Diğer yıllar için → 01.01.<YIL>
  Örnek:
  01.01.2026 ile 04.01.2026

## Header

- Authorization: Bearer <JWT_TOKEN>
- Content-Type: application/json

## Body

{
"input": "finansal rasyo raporu oluştur"
}

input alanı tetikleyici / bağlamsal amaçlıdır.
Tarih bilgisi beklenmez.

## Result (Response)

{
"user_id": 3,
"auto_date_range": "01.01.2026 ile 04.01.2026",
"items": [
"Net_Satışlar",
"Brut_Kar_Marjı",
"Stok Gün Sayısı"
],
"results": {
"Net_Satışlar": 436818681.62,
"Brut_Kar_Marjı": 0.4012,
"Stok Gün Sayısı": 36.93
}
}

## MailLogger (v2.2.0)

API içinde oluşturulan kritik loglar MailLogger tarafından .env içindeki listedeki adreslere gönderilir.
.env:
MAIL_RECIPIENTS=example@gmail.com

Mail gönderen fonksiyon:

- tüm log mesajlarını buffer’da toplar
- endpoint tamamlandığında mail gönderir

## Docker ile Çalıştırma

docker build -t queryrunner-api .
docker run -p 8000:8000 queryrunner-api

## Sürüm Geçmişi

| Versiyon   | Açıklama                                                      |
| ---------- | ------------------------------------------------------------- |
| **v1.0.0** | Statik SQL sorguları                                          |
| **v2.0.0** | Tarih aralıklı sorgu desteği eklendi                          |
| **v2.1.0** | `/query/v2/run-basic` endpoint eklendi (tarihsiz sorgular)    |
| **v2.2.0** | Note alanı, MailLogger, docstringler, güvenlik geliştirmeleri |

## Katkı Sağlama

Pull request ve issue açarak katkıda bulunabilirsiniz.

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
