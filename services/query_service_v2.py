"""
Query Service V2

Provides helper to run predefined SQL queries stored in the database (ChefPanel_test.dbo.nly_sql_api)
and execute them against the target database (V3_CHEFSEASONS). The main exported function
`run_query_basic`:

- Fetches the SQL text by `key` from the nly_sql_api table.
- Executes the retrieved SQL text using the database layer.
- Logs progress and errors via MailLogger and the module logger.
- Raises fastapi.HTTPException for client/errors and 500 for unexpected failures.

Return value contract:
- On success: returns the dict produced by `run_sql` (should contain result rows or metadata).
- On SQL error: raises HTTPException(status_code=400, detail=...).
- If key not found: raises HTTPException(status_code=404, detail=...).

Notes:
- This module does not perform SQL templating or parameter substitution; ensure queries
  stored in the DB are safe or perform prior sanitization/templating before execution.
- For production, enhance logging, error handling and avoid executing untrusted SQL.
"""

import logging
from fastapi import HTTPException
from database import get_sql_from_table2, run_sql
from utils.mail_logger import MailLogger

logger = logging.getLogger(__name__)

def run_query_basic(key: str):
    """
    Execute a basic predefined SQL query by key.

    Fetches the SQL text from the nly_sql_api table using the provided key,
    executes it against the target database, and returns the result.

    Args:
        key (str): The key to identify the SQL query in the database.

    Returns:
        dict: The result of the SQL execution, containing rows and metadata.

    Raises:
        HTTPException: 404 if key not found, 400 on SQL errors, 500 on unexpected errors.
    """
    MailLogger.add(f"⏵ [run_query_basic] İşlem başladı: key='{key}'")

    try:
        # 1️⃣ SQL metnini ChefPanel_test veritabanından al
        MailLogger.add("   • SQL metni getiriliyor...")
        sql_query = get_sql_from_table2(key)

        if not sql_query:
            MailLogger.add("   ❌ SQL bulunamadı!")
            raise HTTPException(status_code=404, detail=f"'{key}' için SQL bulunamadı.")
        MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
        MailLogger.add(f"   • SQL alındı:\n{sql_query}")

        # 2️⃣ SQL sorgusunu V3_CHEFSEASONS üzerinde çalıştır
        MailLogger.add("   • SQL çalıştırılıyor...")
        result = run_sql(sql_query)

        if "error" in result:
            MailLogger.add(f"   ❌ SQL Hatası: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
        MailLogger.add(f"   • SQL sonucu başarıyla alındı. Rowcount: {result.get('rowcount')}")
        MailLogger.add("⏵ [run_query_basic] Tamamlandı.\n")

        return result

    except HTTPException as e:
        MailLogger.add(f"   ❌ HTTPException: {str(e)}")
        raise e

    except Exception as e:
        MailLogger.add(f"   ❌ Beklenmeyen hata: {str(e)}")
        logger.error(f"[run_query_basic] Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))