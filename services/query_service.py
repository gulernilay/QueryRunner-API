"""
Query Service (v1/v2) - English docstring

Provides helpers to fetch predefined SQL texts from the database (ChefPanel_test.dbo.nly_sql_api),
replace date ranges inside those SQL texts and execute them.

Exports:
- replace_dates_in_sql(sql: str, date_range: str) -> str
    Replace occurrences of dates and BETWEEN ... AND ... patterns in a stored SQL
    text with user-provided start/end dates. Accepts input dates in "DD.MM.YYYY" format
    and converts them to "YYYY-MM-DD" or compact "YYYYMMDD" where applicable.

- run_queries_simple(items: list[str], date_range: str | None)
    For each key in `items`, fetch the SQL from DB, optionally apply date replacements,
    execute the SQL via the database layer and return a dict of results.

Notes:
- This module expects safe SQL stored in the DB. Avoid executing untrusted SQL.
- Error handling logs via MailLogger and returns None for items that fail.
- Date parsing uses datetime.strptime with format "%d.%m.%Y".
"""

import sys
import io
import logging
from database import get_sql_from_table2, run_sql
import re
from datetime import datetime
from utils.mail_logger import MailLogger

# UTF-8 encoding and logging configuration
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def replace_dates_in_sql(sql: str, date_range: str) -> str:
    """
    Replace date occurrences in SQL text with user-provided date range.
    
    Parses a date range string in format "DD.MM.YYYY ile DD.MM.YYYY" and replaces:
    - Single date comparisons (JournalDate = '...') with start date
    - BETWEEN ... AND ... clauses with start and end dates
    
    Supports both quoted ('YYYY-MM-DD') and numeric (YYYYMMDD) date formats.

    Args:
        sql (str): SQL statement containing hardcoded dates to replace.
        date_range (str): Date range in format "DD.MM.YYYY ile DD.MM.YYYY".

    Returns:
        str: SQL statement with dates replaced. Returns original SQL on parse error.
    """
    print("Tarih değiştirme fonksiyonu çağrıldı.")
    try:
        start_str, end_str = [d.strip() for d in date_range.split("ile")]
        start_date = datetime.strptime(start_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        print("Başlangıç tarihi:", start_date)
        end_date = datetime.strptime(end_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        print("Bitiş tarihi:", end_date)
        start_compact = start_date.replace("-", "")
        end_compact = end_date.replace("-", "")

        # 1️⃣ Replace single date comparisons (JournalDate =) with start date
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

        # 2️⃣ Replace BETWEEN clauses with start and end dates
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
    """
    Execute multiple predefined queries by key, optionally with date range substitution.
    
    For each key in the items list:
    1. Fetches the SQL statement from nly_sql_api table.
    2. Optionally replaces dates in the SQL using replace_dates_in_sql.
    3. Executes the SQL and extracts the first column value from the first row.
    4. Returns results mapped by key; None values indicate failures.

    Args:
        items (List[str]): List of query keys to execute (e.g., ["Dönen_Varlıklar"]).
        date_range (Optional[str]): Date range for substitution in format "DD.MM.YYYY ile DD.MM.YYYY".

    Returns:
        dict: Mapping of query keys to result values or None on failure.
              Example: {"Dönen_Varlıklar": 12345, "Kısa_Vadeli_Borçlar": None}
    """
    results = {}

    for item in items:
        try:
            MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
            MailLogger.add(f"⏵ Item işleniyor: {item}")

            sql = get_sql_from_table2(item)
            MailLogger.add(f"   • SQL alındı.")

            if not sql:
                MailLogger.add(f"   • SQL bulunamadı!")
                results[item] = None
                continue

            # Replace dates if date range is provided
            if date_range:
                MailLogger.add(f"   • Tarih aralığı tespit edildi → {date_range}")
                MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                MailLogger.add(f"   • SQL değişmeden önce: {sql}")
                sql = replace_dates_in_sql(sql, date_range)
                MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                MailLogger.add(f"   • SQL değiştirildi → {sql}")
            MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
            MailLogger.add("   • SQL çalıştırılıyor...")
            exec_result = run_sql(sql)

            if exec_result and "rows" in exec_result and len(exec_result["rows"]) > 0:
                value = list(exec_result["rows"][0].values())[0]
                MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                MailLogger.add(f"   • SQL sonucu: {value}")
                results[item] = value
            else:
                MailLogger.add("   • Sonuç yok.")
                results[item] = None

        except Exception as e:
            MailLogger.add(f"   ❌ Hata: {str(e)}")
            results[item] = None

    return results
