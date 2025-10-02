# Sorgu mantığı 
from database import get_sql_from_table2, run_sql

def run_queries(items: list[str]):
    """
    items -> her biri için Tablo2'den SQL çek, çalıştır, sonucu topla.
    Sonuçta hem SQL’i hem de veriyi dönüyoruz (şeffaflık için faydalı).
    """
    results={}
    for item in items:
      print("Sorgulanan item:",item)
      sql = get_sql_from_table2(item)
      if sql:
          results[item] = sql
      else:
            results[item] = None
      exec_result = run_sql(sql)
      if "error" in exec_result:
            results[item] = {"sql": sql, "data": None, "error": exec_result["error"]}
      else:
            results[item] = {"sql": sql, "data": exec_result}
      
    return {
        "results": results   # <-- artık { "Dönen_Varlıklar": "select ...", ... }
    }
    
