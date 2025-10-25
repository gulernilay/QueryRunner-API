from fastapi import FastAPI
from controllers import auth_controller, query_controller , query_controller_v2
# Uygulamayı başlat
app = FastAPI(
    title="QueryRunner API",
    description="Login ve SQL query runner API",
    version="2.0.0"
)

# Controller (Router) bağlantıları
app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
app.include_router(query_controller.router, prefix="/query", tags=["Query"])
app.include_router(query_controller_v2.router, prefix="/query/v2", tags=["Query V2"])

# Sağlık kontrolü için basit endpoint
@app.get("/")
def root():
    return {"message": "QueryRunner API is running 🚀"}

