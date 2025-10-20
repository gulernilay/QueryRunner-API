# Sorgu mantığı
import sys
import io
import logging
from database import get_sql_from_table2, run_sql
import re
from datetime import datetime


# UTF-8 encoding ve logging yapılandırması
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def replace_dates_in_sql(sql: str, date_range: str) -> str:
    """
    Kullanıcının '02.01.2025 ile 31.08.2025' formatındaki tarih aralığını alır,
    SQL içinde geçen '=' ve 'BETWEEN' ifadelerini doğru sırayla değiştirir:
    - İlk '=' veya 'JournalDate =' → başlangıç tarihi
    - 'BETWEEN ... AND ...' → başlangıç ve bitiş tarihi
    """
    try:
        start_str, end_str = [d.strip() for d in date_range.split("ile")]
        start_date = datetime.strptime(start_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        start_compact = start_date.replace("-", "")
        end_compact = end_date.replace("-", "")

        # 1️⃣ "aj.JournalDate =" gibi tekil tarihleri başlangıç tarihiyle değiştir
        sql = re.sub(
            r"(JournalDate\s*=\s*)'20\d{2}[-]?\d{2}[-]?\d{2}'",
            fr"\1'{start_date}'",
            sql
        )
        sql = re.sub(
            r"(JournalDate\s*=\s*)20\d{6}",
            fr"\1{start_compact}",
            sql
        )

        # 2️⃣ BETWEEN ifadelerini başlangıç ve bitiş tarihleriyle değiştir
        sql = re.sub(
            r"BETWEEN\s*'20\d{2}[-]?\d{2}[-]?\d{2}'\s*AND\s*'20\d{2}[-]?\d{2}[-]?\d{2}'",
            f"BETWEEN '{start_date}' AND '{end_date}'",
            sql
        )
        sql = re.sub(
            r"BETWEEN\s*20\d{6}\s*AND\s*20\d{6}",
            f"BETWEEN {start_compact} AND {end_compact}",
            sql
        )

        return sql

    except Exception as e:
        print(f"Tarih değiştirme hatası: {e}")
        return sql
    

def run_queries_simple(items: list[str], date_range: str = None):
    results = {}

    for item in items:
        try:
            logger.info(f"Sorgulanan item: {item}")
            sql = get_sql_from_table2(item)
            if not sql:
                results[item] = None
                continue

            # Tarih aralığı varsa SQL'i güncelle
            if date_range:
                sql = replace_dates_in_sql(sql, date_range)
                logger.info(f"Güncellenmiş SQL ({item}): {sql}")

            exec_result = run_sql(sql)
            # Data’yı sadeleştir
            if (
                exec_result
                and "rows" in exec_result
                and len(exec_result["rows"]) > 0
            ):
                first_row = exec_result["rows"][0]
                # ilk kolonun değerini al
                value = list(first_row.values())[0]
                results[item] = value
            else:
                results[item] = None

        except Exception as e:
            results[item] = None
            logger.error(f"{item} sorgusunda hata: {e}")

    return results
