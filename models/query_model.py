# Key- Prompt-Query database model
from pydantic import BaseModel
from typing import List

# Kullanıcıdan gelen query request
class QueryRequest(BaseModel):
    token: str
    items: List[str]

# DB'den Tablo2 için gelen mapping
class QueryMapping(BaseModel):
    key: str
    sql_query: str

# API’nin döndüreceği response
class QueryResponse(BaseModel):
    results: dict