"""
Query Controller V2 

Provides HTTP endpoints to execute basic (stateless) predefined SQL queries stored in the database.
Unlike query_controller.py, this controller does NOT accept date parameters; it runs fixed queries
as-is from the nly_sql_api table. Ideal for IK summaries, dashboards and other static reports.

Authentication via JWT bearer token is required for all endpoints.

Endpoints:
- POST /run-basic
    Execute a single predefined SQL query by key. Returns the full result set including
    column names, row count and result rows.

Notes:
- All endpoints require valid JWT authentication via Authorization header.
- The `key` field must match a record in ChefPanel_test.dbo.nly_sql_api.
- Requests and responses are logged via MailLogger for auditing.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.query_service_v2 import run_query_basic
from utils.jwt_utils import verify_jwt
from models.query_model import QueryRunBasicRequest
from utils.mail_logger import MailLogger

router = APIRouter()
security = HTTPBearer()

@router.post("/run-basic")
def run_basic_query(
    body: QueryRunBasicRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute a basic (stateless) predefined SQL query by key.
    
    Validates JWT token, fetches and executes a stored SQL query from the database
    without any date parameter substitution. Returns full result set with columns,
    row count and rows. All activity is logged via MailLogger for audit trail.

    Args:
        body (QueryRunBasicRequest): Request containing the query key.
        credentials (HTTPAuthorizationCredentials): JWT bearer token from Authorization header.

    Returns:
        dict: {
            "user_id": int,
            "key": str,
            "rowcount": int,
            "data": list[dict]  # result rows
        }

    Raises:
        HTTPException: 401 if token invalid, 404 if key not found, 500 on execution errors.
    """
    # Mail Logger is started
    MailLogger.start("/query/v2/run-basic")
    MailLogger.add("1) Endpoint çağrısı alındı.")

    # Token validation
    MailLogger.add("2) Token doğrulaması başladı.")
    token = credentials.credentials
    payload = verify_jwt(token)

    if not payload:
        MailLogger.add(" Token doğrulaması başarısız!")
        MailLogger.send()
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = payload.get("user_id")
    MailLogger.add(f"3) Token doğrulandı → User ID: {user_id}")

    MailLogger.add(f"4) Gelen key: {body.key}")

    try:
        MailLogger.add("5) SQL çalıştırma başlatıldı...")
        result = run_query_basic(body.key)
        MailLogger.add(f"6) SQL sonucu alındı. Rowcount={result.get('rowcount')}")
        MailLogger.add("7) Endpoint başarıyla tamamlandı.")

        MailLogger.send()

        return {
            "user_id": user_id,
            "key": body.key,
            "rowcount": result.get("rowcount"),
            "data": result.get("rows")
        }

    except Exception as e:
        MailLogger.add(f" Hata oluştu: {str(e)}")
        MailLogger.send()
        raise
