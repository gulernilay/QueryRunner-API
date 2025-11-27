"""
Run Raw SQL Service (English docstring)

Provides a service to execute raw SELECT and WITH (CTE) SQL statements received from request bodies.
Security: only SELECT and WITH statements are allowed — any non-SELECT/non-WITH SQL will be rejected.
The function returns a dict containing columns, rowcount and rows when successful.
On SQL or execution errors an HTTPException is raised with an appropriate status code.

Exports:
- run_raw_sql(sql: str) -> dict
    Execute a raw SELECT or WITH SQL statement against the V3_CHEFSEASONS database.
    Returns column names, row count and result rows.

Notes:
- Do NOT use this service to execute untrusted or user-supplied DDL/DML statements.
- Prefer prepared statements or parameterized queries for dynamic inputs.
- All activity is logged via MailLogger for audit trail and debugging.
"""

import logging
from fastapi import HTTPException
from database import connect2
from utils.mail_logger import MailLogger

logger = logging.getLogger(__name__)

def run_raw_sql(sql: str):
    """
    Execute a raw SELECT or WITH (CTE) SQL statement directly.
    
    Security: Only SELECT and WITH statements are permitted. Any DDL/DML
    statements (INSERT, UPDATE, DELETE, DROP, etc.) will be rejected.
    
    The function connects to the V3_CHEFSEASONS database, executes the provided
    SQL, retrieves all rows and column metadata, and returns them as a structured dict.
    All operations are logged via MailLogger.

    Args:
        sql (str): SQL text to execute. Must start with SELECT or WITH.

    Returns:
        dict: {
            "columns": list[str],      # Column names from result set
            "rowcount": int,            # Number of rows returned
            "rows": list[dict]          # Result rows as list of dicts
        }

    Raises:
        HTTPException: 
            - 400 if non-SELECT/non-WITH statement detected.
            - 500 on SQL execution errors or database connection failures.
    """

    MailLogger.add("   → [run_raw_sql] Raw SQL execution started.")

    # Security check: only SELECT and WITH (CTE) are allowed
    if not sql.strip().lower().startswith(("select", "with")):
        MailLogger.add("   ❌ Non-SELECT/WITH SQL detected! Request rejected.")
        raise HTTPException(status_code=400, detail="Only SELECT and WITH statements are allowed.")

    try:
        MailLogger.add("   • Connecting to database...")
        conn = connect2()

        cur = conn.cursor()
        MailLogger.add("   • Executing SQL...")

        cur.execute(sql)

        # Extract column names and result rows
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, r)) for r in rows]

        MailLogger.add(f"   • SQL executed successfully. Result count: {len(data)} rows")

        cur.close()
        conn.close()

        MailLogger.add("   → [run_raw_sql] Completed.\n")

        return {
            "columns": cols,
            "rowcount": len(data),
            "rows": data
        }

    except HTTPException as e:
        MailLogger.add(f"   ❌ HTTP Exception: {str(e)}")
        raise

    except Exception as e:
        MailLogger.add(f"   ❌ SQL Error: {str(e)}")
        logger.error(f"Raw SQL error: {e}")
        raise HTTPException(status_code=500, detail=str(e))