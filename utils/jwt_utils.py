# JWT üretme/doğrulama işlemleri

import jwt
from datetime import datetime, timedelta

SECRET_KEY = "supersecret"  # .env dosyasına taşı
ALGORITHM = "HS256"

def generate_jwt(data: dict, expires_delta: int = 30):
    """Access token üretir"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return None
    
def verify_jwt(token: str):
    """Access token doğrulaması yapar"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload   # içinde user_id vs. olacak
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None