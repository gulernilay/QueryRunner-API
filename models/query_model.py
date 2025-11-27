"""
Query Models (English docstring)

Pydantic models for query-related request and response validation.
These models enforce type safety and auto-generate OpenAPI documentation.

Models:
- QueryRequest: Legacy model for query requests with token and items list.
- QueryMapping: Database mapping for key-to-SQL associations from nly_sql_api table.
- QueryResponse: Generic response wrapper for query execution results.
- QueryRunBasicRequest: Request model for basic (stateless) query execution by key.
"""
from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    """Legacy request model for query execution.
    
    Attributes:
        token (str): JWT bearer token for authentication.
        items (List[str]): List of query keys to execute (e.g., ["Dönen_Varlıklar"]).
    """
    token: str
    items: List[str]

class QueryMapping(BaseModel):
    """Database mapping model for query storage.
    
    Represents a record from ChefPanel_test.dbo.nly_sql_api table,
    mapping a query key to its corresponding SQL statement.
    
    Attributes:
        key (str): Unique identifier for the query (e.g., "Dönen_Varlıklar").
        sql_query (str): The SQL statement associated with the key.
    """
    key: str
    sql_query: str

class QueryResponse(BaseModel):
    """Generic response model for query execution results.
    
    Attributes:
        results (dict): Dictionary containing query results, typically
                       mapped by query key to its result value or data.
    """
    results: dict

class QueryRunBasicRequest(BaseModel):
    """Request model for basic (stateless) query execution.
    
    Used for executing predefined queries that do not require date parameter
    substitution (e.g., IK summaries, static reports).
    
    Attributes:
        key (str): Query key to execute (must exist in nly_sql_api table).
    """
    key: str