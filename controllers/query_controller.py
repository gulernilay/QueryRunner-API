# controllers/query_controller.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.query_service import run_queries_simple
from utils.jwt_utils import verify_jwt
from pydantic import BaseModel
from typing import List, Optional

"""
APIRouter → FastAPI’de endpointleri modüler yönetmek için kullanılıyor (controller mantığı).
Depends → Dependency injection. Yani bir endpoint çağrılırken otomatik parametre sağlamak için.
HTTPException → Hata durumlarında HTTP yanıtı döndürmek için.
HTTPBearer → Bearer token (Authorization header’daki JWT) okumak için.
run_queries → Senin services/query_service.py içindeki fonksiyon. Gelen item’lara göre DB’den SQL çekip çalıştırıyor.
verify_jwt → utils/jwt_utils.py içindeki fonksiyon. Token’ın geçerli olup olmadığını kontrol ediyor.
"""

router = APIRouter()
security = HTTPBearer() 

"""
router → Bu controller’ın router’ı. main.py içinde app.include_router() ile bağlanıyor.
security = HTTPBearer() → Header’dan Authorization: Bearer <token> bilgisini okumak için hazır FastAPI helper.
"""
class QueryBody(BaseModel):
    items: List[str]
    Tarih: Optional[str] = None  # örn: "02.01.2025 ile 31.08.2025"


@router.post("/")
def query(
    body: QueryBody,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_jwt(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Tarih parametresi varsa onu da servise gönder
    result = run_queries_simple(body.items, date_range=body.Tarih)
    return result
"""
return {
        "user_id": user_id,
        "sorgu": items,
        "results": result   # <-- artık { "Dönen_Varlıklar": "select ...", ... }
    }
"""    