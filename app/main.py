import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.init_db import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    API для обнаружения и сегментации опухолей головного мозга на МРТ-изображениях.
    
    ## Возможности
    
    * 🔐 Аутентификация пользователей
    * 👥 Управление пользователями
    * 🧠 Анализ МРТ-изображений
    * 📊 Сегментация опухолей
    
    ## Технологии
    
    * FastAPI
    * PyTorch
    * PostgreSQL
    * SQLAlchemy
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники в режиме разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Подключаем роутер API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
    logger.info(f"Email settings: SMTP_HOST={settings.SMTP_HOST}, SMTP_PORT={settings.SMTP_PORT}, SMTP_USER={settings.SMTP_USER}, EMAILS_ENABLED={settings.EMAILS_ENABLED}")
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 