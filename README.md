# QueryRunner API

QueryRunner API, kullanıcı doğrulama ve SQL sorgu çalıştırma işlemleri için geliştirilmiş bir FastAPI tabanlı web servisidir.Yeni sürümle birlikte artık tarih aralıklı sorgular ve tarih parametresi olmadan çalışan statik sorgular da desteklenmektedir.

---

## 🚀 Versiyon

**v2.1.0**

- **v1.0.0** → Statik SQL sorguları
- **v2.0.0** → Dinamik tarih aralıklı sorgular
- **v2.1.0** → Yeni endpoint: `/query/v2/run-basic` (tarihsiz, İK gibi sabit sorgular için)

---

## Özellikler

- Kullanıcı login (JWT token üretimi)
- Token doğrulama
- Tarih aralıklı sorgular (örnek: `"02.01.2025 ile 31.08.2025"`)
- Tarih parametresi olmadan çalışan statik sorgular
- Sağlık kontrolü endpoint (`/`)
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

## Docker ile Çalıştırma

docker build -t queryrunner-api .
docker run -p 8000:8000 queryrunner-api

## Sürüm Geçmişi

| Versiyon   | Açıklama                                                   |
| ---------- | ---------------------------------------------------------- |
| **v1.0.0** | Statik SQL sorguları                                       |
| **v2.0.0** | Tarih aralıklı sorgu desteği eklendi                       |
| **v2.1.0** | `/query/v2/run-basic` endpoint eklendi (tarihsiz sorgular) |

## Katkı Sağlama

Pull request ve issue açarak katkıda bulunabilirsiniz.

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
