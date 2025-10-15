#Token üretme ve doğrulama işlemleri
from utils.jwt_utils import generate_jwt
from database import get_user_by_username
import bcrypt

# Memory dict (örnek, prod'da Redis tercih edilir)
token_store = {}

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username ,password)
    if not user:
        return None
    #if not bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
    #    return None
    return user

def create_token(user_id: int):
    token = generate_jwt({"user_id": user_id})
    token_store[user_id] = token
    return token

def validate_token(user_id: int, token: str):
    return token_store.get(user_id) == token

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username, password)
    if not user:
        return None
    return user
