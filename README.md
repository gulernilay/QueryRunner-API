# QueryRunner API

QueryRunner API, kullanıcı doğrulama ve SQL sorgu çalıştırma işlemleri için geliştirilmiş bir FastAPI tabanlı web servisidir.

## Özellikler

- Kullanıcı login (JWT token üretimi)
- Token doğrulama
- SQL sorgularını çalıştırma
- Sağlık kontrolü endpoint (`/`)

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

## Çalıştırma

Uygulamayı başlatmak için:

```sh
uvicorn main:app --reload
```

API varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır.

## API Endpointleri

- `GET /` : Sağlık kontrolü
- `POST /auth/login` : Kullanıcı girişi
- `POST /query/` : SQL sorgusu çalıştırma

## Katkı Sağlama

Pull request ve issue açarak katkıda bulunabilirsiniz.

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
