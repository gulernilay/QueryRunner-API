# DB bağlantısı
import pyodbc
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def connect():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE_1')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "TrustServerCertificate=yes;"
        "encrypt=yes;"
    )
    return conn

def connect2():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE_2')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "TrustServerCertificate=yes;"
        "encrypt=yes;"
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

    if row and row.sifre == password:  # DÜZ şifre kontrolü
        return {"id": row.id, "username": row.kullanici, "password": row.sifre}
    return None

def get_sql_from_table2(key: str):
    logger.info("get_sql_from_table2 fonksiyonu çağrıldı. Key:", key)
    conn = connect()
    cur = conn.cursor()
    logger.info("Çalışacak sorgu:", "SELECT query FROM ChefPanel_test.dbo.nly_sql_api WHERE key_ = ?", key)
    cur.execute("SELECT query FROM ChefPanel_test.dbo.nly_sql_api WHERE key_ = ?", (key,))
    row = cur.fetchone()
    cur.close(); conn.close()
    
    return row[0] if row else None

def run_sql(sql: str):
    """
    Verilen SQL’i çalıştırır ve sonucu uygun formatta döndürür.
    (Güvenlik için SELECT dışını blokluyoruz.)
    """
    # basit güvenlik: SELECT ile başlamıyorsa çalıştırma
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
            # SELECT değilse buraya düşerdi, ama zaten engelledik
            conn.commit()
            return {"columns": [], "rows": [], "rowcount": cur.rowcount}
    finally:
        cur.close()
        conn.close()