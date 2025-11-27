"""
Query Controller (English docstring)

Provides HTTP endpoints to execute predefined SQL queries stored in the database.
Authentication via JWT bearer token is required for all endpoints.

Endpoints:
- POST /query/
    Execute one or more predefined SQL queries by key. Optionally accepts a date range
    to dynamically replace dates in the stored SQL statements.

Notes:
- All endpoints require valid JWT authentication via Authorization header.
- The `items` field contains a list of query keys (e.g., ["Dönen_Varlıklar", "Kısa_Vadeli_Borçlar"]).
- The optional `Tarih` field accepts a date range in format "DD.MM.YYYY ile DD.MM.YYYY".
- Results are logged via MailLogger for auditing and debugging purposes.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.query_service import run_queries_simple
from utils.jwt_utils import verify_jwt
from pydantic import BaseModel
from typing import List, Optional
import logging
from utils.mail_logger import MailLogger

router = APIRouter()
security = HTTPBearer()

logging.basicConfig(
    filename="queryrunner.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class QueryBody(BaseModel):
    """Request model for query execution.
    
    Attributes:
        items (List[str]): List of query keys to execute (e.g., ["Dönen_Varlıklar"]).
        Tarih (Optional[str]): Optional date range in format "DD.MM.YYYY ile DD.MM.YYYY".
    """
    items: List[str]
    Tarih: Optional[str] = None


@router.post("/query/")
def query(
    body: QueryBody,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute one or more predefined SQL queries by key.
    
    Validates JWT token, fetches and executes stored SQL queries from the database,
    optionally replacing date ranges in the SQL text. Results are logged via MailLogger.

    Args:
        body (QueryBody): Request containing query keys and optional date range.
        credentials (HTTPAuthorizationCredentials): JWT bearer token from Authorization header.

    Returns:
        dict: {
            "user_id": int,
            "items": List[str],
            "result": dict  # key -> query result mapping
        }

    Raises:
        HTTPException: 401 if token invalid, 500 on execution errors.
    """
    MailLogger.start("/query")

    MailLogger.add("1) Endpoint çağrısı alındı.")

    # Token doğrulama
    MailLogger.add("2) Token doğrulaması başladı.")
    token = credentials.credentials
    payload = verify_jwt(token)

    if not payload:
        MailLogger.add("❌ Token doğrulaması başarısız!")
        MailLogger.send()
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = payload.get("user_id")
    MailLogger.add(f"3) Token doğrulandı → User ID: {user_id}")

    # Body bilgisi
    MailLogger.add(f"4) Gelen items listesi: {body.items}")
    if body.Tarih:
        MailLogger.add(f"5) Tarih aralığı: {body.Tarih}")
    else:
        MailLogger.add("5) Tarih aralığı gönderilmedi.")

    try:
        MailLogger.add("6) SQL sorguları çalıştırılıyor...")
        result = run_queries_simple(body.items, date_range=body.Tarih)
        MailLogger.add(f"7) SQL sonuçları: {result}")
        MailLogger.add("8) Endpoint başarıyla tamamlandı.")

        MailLogger.send()

        return {
            "user_id": user_id,
            "items": body.items,
            "result": result
        }

    except Exception as e:
        MailLogger.add(f"❌ Hata: {str(e)}")
        MailLogger.send()
        raise HTTPException(status_code=500, detail=str(e))