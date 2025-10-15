# Sorgu mantığı
import sys
import io
import logging
from database import get_sql_from_table2, run_sql

# UTF-8 encoding ve logging yapılandırması
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def run_queries(items: list[str]):
    """
    items -> her biri için Tablo2'den SQL çek, çalıştır, sonucu topla.
    Sonuçta hem SQL’i hem de veriyi dönüyoruz (şeffaflık için faydalı).
    """
    results = {}

    for item in items:
        try:
            logger.info(f"Sorgulanan item: {item}")
            sql = get_sql_from_table2(item)
            if not sql:
                logger.warning(f"SQL bulunamadı: {item}")
                results[item] = {"sql": None, "data": None, "error": "SQL not found"}
                continue

            exec_result = run_sql(sql)
            if "error" in exec_result:
                logger.error(f"Sorguda hata oluştu ({item}): {exec_result['error']}")
                results[item] = {"sql": sql, "data": None, "error": exec_result["error"]}
            else:
                results[item] = {"sql": sql, "data": exec_result}

        except Exception as e:
            logger.exception(f"❌ Beklenmeyen hata ({item}): {e}")
            results[item] = {"sql": None, "data": None, "error": str(e)}

    return {"results": results}
