# User login and registration db model
from pydantic import BaseModel

# Kullanıcı login request'i için
class UserLogin(BaseModel):
    username: str
    password: str

# DB'den dönen kullanıcı (opsiyonel)
class UserInDB(BaseModel):
    id: int
    username: str
    hashed_password: str
    