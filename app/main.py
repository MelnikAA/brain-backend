from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

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
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер API
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 