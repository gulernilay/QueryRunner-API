"""
QueryRunner API - Main Application 

FastAPI-based REST API for user authentication and SQL query execution.
Provides endpoints for login, executing predefined queries with date parameters,
executing basic (stateless) queries, and running raw SELECT SQL statements.

Architecture:
- Authentication: JWT bearer token-based auth via /auth/login endpoint.
- Query Execution: Multiple endpoints for different query execution patterns:
  * /query/ → Predefined queries with optional date range substitution.
  * /query/v2/ → Basic (stateless) predefined queries without date parameters.
  * /query/raw/ → Raw SELECT SQL execution (user-supplied SQL).

Routes:
- Authentication Controller (/auth)
  * POST /auth/login → User authentication and token generation.

- Query Controller (/query)
  * POST /query/ → Execute predefined queries with optional date range.

- Query Controller V2 (/query/v2)
  * POST /query/v2/run-basic → Execute basic predefined queries (IK, dashboards, etc.).

- Raw Query Controller (/query/raw)
  * POST /query/raw/run-sql → Execute raw SELECT SQL statements.

- Health Check (/)
  * GET / → API health check endpoint.

Configuration:
- Title: QueryRunner API
- Version: 2.0.0
- Security: All endpoints except GET / require JWT bearer token authentication.
"""

from fastapi import FastAPI
from controllers import auth_controller, query_controller, query_controller_v2
from controllers import raw_query_controller
from controllers.query_controller_v3_automated import router as auto_query_router

# Initialize FastAPI application
app = FastAPI(
    title="QueryRunner API",
    description="Login ve SQL query runner API",
    version="2.0.0"
)

# Include route controllers (routers)
app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
app.include_router(query_controller.router, prefix="/query", tags=["Query"])
app.include_router(query_controller_v2.router, prefix="/query/v2", tags=["Query V2"])
app.include_router(raw_query_controller.router, prefix="/query/raw", tags=["Raw SQL"])
app.include_router(auto_query_router, prefix="/query", tags=["Auto Query"])


# Health check endpoint
@app.get("/")
def root():
    """
    Health check endpoint.
    
    Returns a simple JSON response indicating the API is running.
    No authentication required.

    Returns:
        dict: {"message": "QueryRunner API is running 🚀"}
    """
    return {"message": "QueryRunner API is running 🚀"}

