# controllers/query_controller_v2.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.query_service_v2 import run_query_basic
from utils.jwt_utils import verify_jwt
from models.query_model import QueryRunBasicRequest

router = APIRouter()
security = HTTPBearer()

@router.post("/run-basic")
def run_basic_query(
    body: QueryRunBasicRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Yeni v2 endpoint:
    Sadece key alır, nly_sql_api tablosundaki SQL sorgusunu bulur ve çalıştırır.
    """
    token = credentials.credentials
    payload = verify_jwt(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = run_query_basic(body.key)

    return {
        "user_id": user_id,
        "key": body.key,
        "rowcount": result.get("rowcount"),
        "data": result.get("rows")
    }
