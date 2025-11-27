"""
Database Module 

Provides connection management and query execution for the QueryRunner API.
Connects to two SQL Server databases:
1. DB1: Authentication and query metadata storage.
2. DB2: Target database for executing user queries.

Exports:
- connect() -> pyodbc.Connection
    Establish connection to DB1.

- connect2() -> pyodbc.Connection
    Establish connection to DB1.

- get_user_by_username(username: str, password: str) -> dict | None
    Authenticate a user by username and password.

- get_sql_from_table2(key: str) -> str | None
    Fetch a predefined SQL query by key from X table.

- run_sql(sql: str) -> dict
    Execute a SELECT SQL statement and return results with metadata.

Configuration:
- Database credentials are loaded from .env file in project root.
- Required environment variables: DB_SERVER, DB_DATABASE_1, DB_DATABASE_2, DB_USER, DB_PASSWORD.
"""

import pyodbc
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")

if not os.getenv("DB_SERVER"):
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        logger.info(f".env file loaded: {env_path}")
    else:
        logger.warning(f".env file not found: {env_path}")

def connect():
    """
    Establish connection to DB1.
    
    Used for authentication and query metadata operations.
    Raises pyodbc.Error if connection fails.

    Returns:
        pyodbc.Connection: Active database connection with 30-second timeout.
    """
    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE_1')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Connection Timeout=30;"
    )
    return conn

def connect2():
    """
    Establish connection to DB2.
    
    Used for executing user queries and fetching business data.
    Raises pyodbc.Error if connection fails.

    Returns:
        pyodbc.Connection: Active database connection with 30-second timeout.
    """
    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE_2')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Connection Timeout=30;"
    )
    return conn

def get_user_by_username(username: str, password: str):
    """
    Authenticate a user by username and password.
    
    Queries the Y table in DB1 and returns
    the user record if credentials match.

    Args:
        username (str): Username to authenticate.
        password (str): Plaintext password to verify.

    Returns:
        dict | None: User dict with keys {id, username, password} on success,
                     None if user not found or credentials invalid.
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM ChefPanel_test.dbo.skymod_api_users WHERE kullanici = ? AND sifre = ?",
        (username, password)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and row.sifre == password:
        return {"id": row.id, "username": row.kullanici, "password": row.sifre}
    return None

def get_sql_from_table2(key: str):
    """
    Fetch a predefined SQL query by key from nly_sql_api table.
    
    Queries the nly_sql_api table in ChefPanel_test to retrieve the SQL statement
    associated with the given key. Used to execute parameterized/template queries.

    Args:
        key (str): Query key identifier (e.g., "Dönen_Varlıklar").

    Returns:
        str | None: SQL query text on success, None if key not found.
    """
    logger.info(f"get_sql_from_table2 function called. Key: {key}")
    conn = connect()
    cur = conn.cursor()
    logger.info(f"Executing query: SELECT query FROM ChefPanel_test.dbo.nly_sql_api WHERE key_ = '{key}'")
    cur.execute("SELECT query FROM ChefPanel_test.dbo.nly_sql_api WHERE key_ = ?", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def run_sql(sql: str):
    """
    Execute a SELECT SQL statement and return results with metadata.
    
    Security: Only SELECT statements are allowed. Any non-SELECT SQL (DDL, DML)
    will be rejected with an error response.
    
    Executes the SQL against V3_CHEFSEASONS database, retrieves all rows and
    column metadata, and returns them in a structured dict format.

    Args:
        sql (str): SELECT SQL statement to execute.

    Returns:
        dict: {
            "columns": list[str],      # Column names
            "rows": list[dict],        # Result rows as list of dicts
            "rowcount": int            # Number of rows returned
        }
        or on error:
        dict: {
            "error": str  # Error message
        }
    """
    # Security: Only SELECT statements allowed
    if not sql.strip().lower().startswith("select"):
        return {"error": "Only SELECT statements are allowed."}

    conn = connect2()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        # SELECT queries will have description metadata
        if cur.description:
            cols = [c[0] for c in cur.description]
            rows = cur.fetchall()
            data = [dict(zip(cols, r)) for r in rows]
            return {"columns": cols, "rows": data, "rowcount": len(data)}
        else:
            # Non-SELECT would reach here (but blocked above)
            conn.commit()
            return {"columns": [], "rows": [], "rowcount": cur.rowcount}
    finally:
        cur.close()
        conn.close()