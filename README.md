# QueryRunner API

QueryRunner API, kullanıcı doğrulama, kayıtlı SQL key’leri çalıştırma ve güvenli raw SQL yürütme işlemleri için geliştirilmiş bir FastAPI tabanlı web servisidir.  
Yeni sürümle birlikte gelişmiş güvenlik filtresi, MailLogger ile e-mail log gönderimi, `/run-sql` endpointine `note` alanı, docstring iyileştirmeleri ve SQL izinlerinin genişletilmesi eklenmiştir.

---

## 🚀 Versiyon

**v2.2.0 (Güncel Sürüm)**

- **v1.0.0** → Statik SQL sorguları
- **v2.0.0** → Dinamik tarih aralıklı SQL sorguları
- **v2.1.0** → `/query/v2/run-basic` (tarihsiz, statik sorgular)
- **v2.2.0** →
  - `/run-sql` → `note` alanı eklendi
  - Gelişmiş Raw SQL güvenliği (SELECT + WITH dışı bloklama)
  - MailLogger (SMTP log gönderimi)
  - Tüm .py dosyalarına docstring eklemeleri
  - startswith() bug fix
  - Genel API stabilite iyileştirmeleri

---

## Özellikler

- JWT tabanlı kullanıcı doğrulama
- Token doğrulama mekanizması
- Kayıtlı SQL sorgularını `items` veya `key` ile çalıştırma
- Tarih aralığı destekli sorgular (örnek: `"02.01.2025 ile 31.08.2025"`)
- Tarihsiz statik sorgular (İK gibi)
- Gelişmiş SELECT/WITH güvenlik filtresi
- Raw SQL isteklerine opsiyonel `note` alanı (log amaçlı)
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

   MAIL_RECIPIENTS=example@chefseasons.com

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

   database.py dosyasındaki get_sql_from_table2() fonksiyonu için kullanılacak Query tablosu (sorgu ve prompt saklanır):

   ```sql
   CREATE TABLE [ChefPanel_test].[dbo].[nly_sql_api] (
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

Desteklenen:
✔ SELECT
✔ WITH

Bloklanan:

❌ INSERT, UPDATE, DELETE
❌ DROP, ALTER, TRUNCATE
❌ EXEC
❌ CREATE
❌ MERGE
❌ SELECT dışı tüm komutlar

## Body örneği:

{
"sql": "SELECT _ FROM [Table Name] _;",
"note": "İK raporu için test sorgusu" #note alanı sadece loglama içindir.
}

## Yanıt:

{
"user_id": 12,
"key": "IK_Aylik_Ozet",
"rowcount": 24,
"data": [...]
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
