"""

Query Controller V3 Automated

Provides HTTP endpoints for automated query execution with automatic date range calculation.

Authentication via JWT bearer token is required for all endpoints.

Endpoints:
- POST /query_automatized
    Execute multiple queries with automatic date range. Returns results for each query key.

Notes:
- Date range is calculated automatically based on current year.
- For 2025, starts from 02.01.2025, otherwise from 01.01.year.
- All activity is logged via MailLogger for auditing.

"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt_utils import verify_jwt
from utils.mail_logger import MailLogger
from services.query_service import run_queries_simple
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

class AutoQueryBody(BaseModel):
    """Request model for automated query.

    Attributes:
        items (List[str]): List of query keys to execute.
    """
    items: List[str]

def get_auto_date_range():
    """Calculate automatic date range for queries.

    Returns a date range string based on current year.
    For 2025, starts from 02.01.2025, otherwise from 01.01.year.

    Returns:
        str: Date range in format "start_date ile end_date"
    """
    today = datetime.today()
    year = today.year

    end_date = today.strftime("%d.%m.%Y")

    # Special rule: For 2025, start from 02.01.2025
    if year == 2025:
        start_date = "02.01.2025"
    else:
        start_date = f"01.01.{year}"

    return f"{start_date} ile {end_date}"

@router.post("/query_automatized")
def auto_query_handler(
    body: AutoQueryBody,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Handle automated query execution with automatic date range.

    Validates JWT token, calculates automatic date range, executes multiple queries,
    and returns results. All activity is logged via MailLogger.

    Args:
        body (AutoQueryBody): Request containing list of query keys.
        credentials (HTTPAuthorizationCredentials): JWT bearer token from Authorization header.

    Returns:
        dict: {
            "user_id": int,
            "auto_date_range": str,
            "items": List[str],
            "results": dict  # query results
        }

    Raises:
        HTTPException: 401 if token invalid, 500 on execution errors.
    """
    # --- Mail Logger Start ---
    MailLogger.start("/query/query_automatized")
    MailLogger.add(" Endpoint çağrıldı: /query/query_automatized")
    MailLogger.add(f" Alınan veri: {body.items}")

    try:
        # JWT verification
        token = credentials.credentials
        payload = verify_jwt(token)

        if not payload:
            MailLogger.add(" Yetkilendirme başarısız! Token geçersiz.")
            MailLogger.send()
            raise HTTPException(status_code=401, detail="Unauthorized")

        user_id = payload.get("user_id")
        MailLogger.add(f" Kullanıcı doğrulandı. user_id: {user_id}")

        # Automatic date calculation
        date_range = get_auto_date_range()
        MailLogger.add(f" Otomatik tarih aralığı oluşturuldu: {date_range}")
        print(f"[AUTO QUERY] Otomatik tarih aralığı: {date_range}")

        # Execute query
        result = run_queries_simple(body.items, date_range=date_range)
        MailLogger.add(" SQL sorguları başarıyla çalıştırıldı.")
        MailLogger.add(f" Dönen sonuçlar: {list(result.keys())}")

        # Send mail
        MailLogger.send()

        return {
            "user_id": user_id,
            "auto_date_range": date_range,
            "items": body.items,
            "results": result
        }

    except Exception as e:
        MailLogger.add(f" Hata oluştu: {str(e)}")
        MailLogger.send()
        raise
