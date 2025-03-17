from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from app.config import settings
from app.routers import health, whatsapp
from app.database.init_db import create_tables

# Configurar logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG_MODE else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Inicializar tablas de base de datos (esto se puede comentar después de la primera ejecución)
# o preferiblemente usar Alembic para migraciones
create_tables()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Whats2Want",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

# Incluir routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(whatsapp.router, prefix="/api/v1")

if __name__ == "__main__":
    port = int(settings.PORT) if settings.PORT else 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=settings.DEBUG_MODE)