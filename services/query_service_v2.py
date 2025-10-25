# services/query_service_v2.py

import logging
from fastapi import HTTPException
from database import get_sql_from_table2, run_sql

logger = logging.getLogger(__name__)

def run_query_basic(key: str):
    """
    Sadece key alır, nly_sql_api tablosundaki sorguyu bulur ve çalıştırır.
    """
    try:
        # 1️⃣ SQL metnini ChefPanel_test veritabanından al
        sql_query = get_sql_from_table2(key)
        if not sql_query:
            raise HTTPException(status_code=404, detail=f"'{key}' için SQL bulunamadı.")

        logger.info(f"[run_query_basic] SQL sorgusu alındı: {sql_query}")

        # 2️⃣ SQL sorgusunu V3_CHEFSEASONS üzerinde çalıştır
        result = run_sql(sql_query)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"[run_query_basic] Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))
