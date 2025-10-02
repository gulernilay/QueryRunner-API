#Login işlemleri
"""
Mantık:

Kullanıcı POST /login ile kullanıcı adı & şifre gönderir.

DB’de doğrulanır.

JWT Bearer Token üretilir.

Token bellekte (örneğin Redis, memory dict) tutulur → ileride karşılaştırma yapılacak.

"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.auth_service import authenticate_user, create_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user["id"])
    return {"access_token": token, "token_type": "bearer"}
