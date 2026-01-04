"""
Raw Query Controller 

Provides HTTP endpoints to execute raw SELECT SQL statements.
Authentication via JWT bearer token is required for all endpoints.

Endpoints:
- POST /run-sql
    Execute a raw SELECT SQL statement. Request body contains the SQL text
    and an optional note field for user context/logging.

Notes:
- All endpoints require valid JWT authentication via Authorization header.
- Only SELECT statements are allowed; DDL/DML will be rejected by the service layer.
- Responses include column names, row count and result rows on success.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from utils.jwt_utils import verify_jwt
from services.run_raw_sql_service import run_raw_sql
from utils.mail_logger import MailLogger   # <-- EKLENDİ
from typing import Optional
from typing import Union, List

router = APIRouter()
security = HTTPBearer()

class RawSQLRequest(BaseModel):
    """Request model for raw SQL execution.
    
    Attributes:
        sql (str): SELECT SQL statement to execute.
        note (Optional[str]): Optional context or comment about the query.
    """
    sql: Union[str, List[str]]
    note: Optional[str] = None   # kullanıcı isterse ek bilgi gönderebilir

@router.post("/run-sql")
def run_raw_sql_endpoint(
    body: RawSQLRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute one or multiple raw SELECT SQL statements.

    Supports:
    - Single SQL string
    - Multiple SQL strings (list)

    Validates JWT token, logs the request via MailLogger, and executes
    the SQL statement(s). Returns columns, row count and result rows
    for each statement.

    Args:
        body (RawSQLRequest): Request containing SQL text (str or list[str]) and optional note.
        credentials (HTTPAuthorizationCredentials): JWT bearer token from Authorization header.

    Returns:
        dict: {
            "results": [
                {
                    "columns": list[str],
                    "rowcount": int,
                    "rows": list[dict]
                },
                ...
            ]
        }

    Raises:
        HTTPException: 401 if token invalid,
                       400 if non-SELECT SQL,
                       500 on execution errors.
    """
    MailLogger.start("/query/raw/run-sql")
    MailLogger.add(f"⏵ [run_raw_sql_endpoint] POST /query/raw/run-sql çağrıldı.")
    if body.note:
        MailLogger.add(f"   • SORU : {body.note}")

    # JWT doğrulama
    try:
        payload = verify_jwt(credentials.credentials)
        user_id = payload.get("user_id")
        MailLogger.add(f"Token doğrulandı. user_id: {user_id}")
    except Exception as e:
        MailLogger.add(f"Token hatası: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

    # ---------------------------------------------------
    #  SQL input type: string → single SQL
    # ---------------------------------------------------
    if isinstance(body.sql, str):
        MailLogger.add(f"Tek SQL çalıştırılacak:\n{body.sql}")
        if body.note:
            MailLogger.add(f"Not: {body.note}")

        result = run_raw_sql(body.sql)
        MailLogger.add(f"  Başarılı. Rowcount: {result.get('rowcount')}")
        MailLogger.add(" [run_raw_sql_endpoint] Tamamlandı.\n")
        MailLogger.send() 
        return {
            "user_id": user_id,
            "results": [result]
        }

    # ---------------------------------------------------
    # SQL input type: list→ multiple SQL
    # ---------------------------------------------------
    results = []
    MailLogger.add(f"Çoklu SQL listesi tespit edildi. Adet: {len(body.sql)}")

    for index, sql_text in enumerate(body.sql):
        MailLogger.add(f"[{index}] SQL çalıştırılacak:\n{sql_text}")

        try:
            r = run_raw_sql(sql_text)
            results.append({
                "index": index,
                "columns": r.get("columns"),
                "rowcount": r.get("rowcount"),
                "rows": r.get("rows")
            })
            MailLogger.add(f"     → [{index}] OK. Rowcount: {r.get('rowcount')}")
        except Exception as e:
            MailLogger.add(f"     → [{index}] Hata: {str(e)}")
            results.append({
                "index": index,
                "error": str(e)
            })

    MailLogger.add("⏵ [run_raw_sql_endpoint] Çoklu SQL tamamlandı.\n")
    MailLogger.send() 
    return {
        "user_id": user_id,
        "results": results
    }