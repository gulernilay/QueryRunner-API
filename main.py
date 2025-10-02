from fastapi import FastAPI
from controllers import auth_controller, query_controller

# Uygulamayı başlat
app = FastAPI(
    title="QueryRunner API",
    description="Login ve SQL query runner API",
    version="1.0.0"
)

# Controller (Router) bağlantıları
app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
app.include_router(query_controller.router, prefix="/query", tags=["Query"])

# Sağlık kontrolü için basit endpoint
@app.get("/")
def root():
    return {"message": "QueryRunner API is running 🚀"}

