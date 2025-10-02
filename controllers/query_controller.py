# controllers/query_controller.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.query_service import run_queries
from utils.jwt_utils import verify_jwt
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

@router.post("/")
def query(
    items: list[str], 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Header'dan token al
    token = credentials.credentials
    payload = verify_jwt(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Token içindeki user_id
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Sorguları çalıştır
    result = run_queries(items)
    return result
"""
return {
        "user_id": user_id,
        "sorgu": items,
        "results": result   # <-- artık { "Dönen_Varlıklar": "select ...", ... }
    }
"""    