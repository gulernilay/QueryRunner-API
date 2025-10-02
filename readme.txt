Kullanıcı Login Endpoint’i (Authentication) 
Mantık:

Kullanıcı POST /login ile kullanıcı adı & şifre gönderir.

DB’de doğrulanır.

JWT Bearer Token üretilir.

Token bellekte (örneğin Redis, memory dict) tutulur → ileride karşılaştırma yapılacak.,


1. auth_controller.py
2. auth_service.py
3. utils/jwt_utils.py 

İkinci Endpoint – Query Çalıştırma
Mantık:

Kullanıcı POST /query ile body’de stringler gönderir (dönen varlıklar, stoklar, vs).

Her string, Tablo2’deki key ile eşleşir → SQL cümlesi çıkar.

Aynı DB’ye bağlanıp sorgu çalıştırılır.

Dönen sonuçlar ara tabloda toplanır → JSON olarak döner.


1.query_controller.py
2.query_service.py

🔹 Çalışma Akışı

Kullanıcı POST /login → DB kontrolü → JWT token üretilir.

Kullanıcı POST /query → body:

{
  "user_id": 1,
  "token": "xxxx",
  "items": ["dönen varlıklar", "stoklar"]
}


Her bir item için Tablo2’den SQL alınır, çalıştırılır.

Sonuç JSON döner:

{
  "results": {
    "dönen varlıklar": 12345,
    "stoklar": 56789
  }
}

