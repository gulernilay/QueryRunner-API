"""
Query Service (v1/v2) 

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

SPECIAL_DAY_BASED_ITEMS = {
    "Nakit_Donusum_Suresi",
    "Stok Gün Sayısı",
    "Tahsil Süresi (gün)",
    "Borc_Odeme_Suresi",
}

def get_day_of_year_from_range(date_range: str) -> int:
    """
    Extract day of year from the end date in the date range.

    Args:
        date_range (str): Date range in format "DD.MM.YYYY ile DD.MM.YYYY".

    Returns:
        int: Day of year for the end date (1-366).
    """
    _, end_str = [d.strip() for d in date_range.split("ile")]
    end_date = datetime.strptime(end_str, "%d.%m.%Y")
    return end_date.timetuple().tm_yday

def replace_day_constants(sql: str, day_of_year: int) -> str:
    """
    SQL içinde 365 / 365.0 / 180 / 180.0 -> day_of_year
    """
    sql = re.sub(r"\b365(\.0)?\b", str(day_of_year), sql)
    sql = re.sub(r"\b180(\.0)?\b", str(day_of_year), sql)
    return sql


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
    print("Date replacement function called.")
    try:
        start_str, end_str = [d.strip() for d in date_range.split("ile")]
        start_date = datetime.strptime(start_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        print("Start date:", start_date)
        end_date = datetime.strptime(end_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        print("End date:", end_date)
        start_compact = start_date.replace("-", "")
        end_compact = end_date.replace("-", "")

        # Replace single date comparisons (JournalDate =) with start date
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

        # Replace BETWEEN clauses with start and end dates
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
        print(f"Date replacement error: {e}")
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

    day_of_year = None
    if date_range:
        day_of_year = get_day_of_year_from_range(date_range)
        MailLogger.add(f"End date calculated as day {day_of_year} of the year.")

    for item in items:
        try:
            MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
            MailLogger.add(f"⏵ Processing item: {item}")

            sql = get_sql_from_table2(item)
            MailLogger.add(f"   • SQL retrieved.")

            if not sql:
                MailLogger.add(f"   • SQL not found!")
                results[item] = None
                continue

            # Replace dates if date range is provided
            if date_range:
                MailLogger.add(f"   • Date range detected → {date_range}")
                MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                MailLogger.add(f"   • SQL before change: {sql}")
                sql = replace_dates_in_sql(sql, date_range)
                MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                MailLogger.add(f"   • SQL değiştirildi → {sql}")
                # SADECE 4 ITEM için: 365 / 180 → bitiş gününün yıl içindeki sırası
                if day_of_year and item in SPECIAL_DAY_BASED_ITEMS:
                    MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                    MailLogger.add(
                        f" Constants 365/180 updated to {day_of_year} for {item}."
                    )
                    sql = replace_day_constants(sql, day_of_year)
                    MailLogger.add(f"• SQL updated for 4 different items → {sql}")
            MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
            MailLogger.add("   • Executing SQL...")
            exec_result = run_sql(sql)

            if exec_result and "rows" in exec_result and len(exec_result["rows"]) > 0:
                value = list(exec_result["rows"][0].values())[0]
                MailLogger.add("⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵⏵")
                MailLogger.add(f"   • SQL result: {value}")
                results[item] = value
            else:
                MailLogger.add("   • No result.")
                results[item] = None

        except Exception as e:
            MailLogger.add(f"   ❌ Error: {str(e)}")
            results[item] = None

    return results
