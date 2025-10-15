import pyodbc
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, "..", ".env")


if not os.getenv("DB_SERVER"):
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        logger.info(f".env dosyası yüklendi: {env_path}")
    else:
        logger.warning(f".env dosyası bulunamadı: {env_path}")

def connect():
    """ChefPanel_test veritabanına bağlanıyor."""
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
    """V3_CHEFSEASONS veritabanına bağlantı sağlandı."""
    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE_2')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Connection Timeout=30;"
    )
    return conn



def get_user_by_username(username: str , password: str):
    conn = connect()
    if conn is True:
        "Bağlantı başarılı"
    else:
        "Bağlantı başarısız"
    cur = conn.cursor()
    cur.execute(
    "SELECT * FROM ChefPanel_test.dbo.skymod_api_users WHERE kullanici = ? AND sifre = ?",
    (username, password)
    )
    row = cur.fetchone()
    cur.close(); conn.close()

    if row and row.sifre == password: 
        return {"id": row.id, "username": row.kullanici, "password": row.sifre}
    return None

def get_sql_from_table2(key: str):
    logger.info("get_sql_from_table2 fonksiyonu . Key:", key)
    conn = connect()
    cur = conn.cursor()
    logger.info("Başlatılacak sorgu:", "SELECT query FROM ChefPanel_test.dbo.nly_sql_api WHERE key_ = ?", key)
    cur.execute("SELECT query FROM ChefPanel_test.dbo.nly_sql_api WHERE key_ = ?", (key,))
    row = cur.fetchone()
    cur.close(); conn.close()

    return row[0] if row else None

def run_sql(sql: str):
    """
    Verilen SQLâ€™i Ã§alÄ±ÅŸtÄ±rÄ±r ve sonucu uygun formatta dÃ¶ndÃ¼rÃ¼r.
    (GÃ¼venlik iÃ§in SELECT dÄ±ÅŸÄ±nÄ± blokluyoruz.)
    """
    # basit gÃ¼venlik: SELECT ile baÅŸlamÄ±yorsa Ã§alÄ±ÅŸtÄ±rma
    if not sql.strip().lower().startswith("select"):
        return {"error": "Only SELECT statements are allowed."}

    conn = connect2()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        # SELECT ise description dolu olur
        if cur.description:
            cols = [c[0] for c in cur.description]
            rows = cur.fetchall()
            data = [dict(zip(cols, r)) for r in rows]
            return {"columns": cols, "rows": data, "rowcount": len(data)}
        else:
            # SELECT deÄŸilse buraya dÃ¼ÅŸerdi, ama zaten engelledik
            conn.commit()
            return {"columns": [], "rows": [], "rowcount": cur.rowcount}
    finally:
        cur.close()
        conn.close()