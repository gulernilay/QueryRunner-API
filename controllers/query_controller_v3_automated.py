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
    items: List[str]

def get_auto_date_range():
    today = datetime.today()
    year = today.year

    end_date = today.strftime("%d.%m.%Y")

    # Özel kural: 2025 yılı için başlangıç 02.01.2025
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
    # --- Mail Logger Başlangıcı ---
    MailLogger.start("/query/query_automatized")
    MailLogger.add(" Endpoint çağrıldı: /query/query_automatized")
    MailLogger.add(f" Gelen Items: {body.items}")

    try:
        # JWT doğrulama
        token = credentials.credentials
        payload = verify_jwt(token)

        if not payload:
            MailLogger.add(" Yetkilendirme başarısız! Token geçersiz.")
            MailLogger.send()
            raise HTTPException(status_code=401, detail="Unauthorized")

        user_id = payload.get("user_id")
        MailLogger.add(f" Kullanıcı doğrulandı. user_id: {user_id}")

        # Otomatik tarih hesaplama
        date_range = get_auto_date_range()
        MailLogger.add(f" Otomatik tarih aralığı oluşturuldu: {date_range}")
        print(f"[AUTO QUERY] Otomatik tarih aralığı: {date_range}")

        # Sorguyu çalıştır
        result = run_queries_simple(body.items, date_range=date_range)
        MailLogger.add(" SQL sorguları başarıyla çalıştırıldı.")
        MailLogger.add(f" Dönen sonuçlar: {list(result.keys())}")

        # Mail gönder
        MailLogger.send()

        return {
            "user_id": user_id,
            "auto_date_range": date_range,
            "items": body.items,
            "results": result
        }

    except Exception as e:
        MailLogger.add(f"🔥 HATA oluştu: {str(e)}")
        MailLogger.send()
        raise
