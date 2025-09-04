"""
Основной модуль приложения AudioScrobeAI.

Этот модуль содержит FastAPI приложение для обработки аудиофайлов,
транскрибации, переводов и суммаризации с использованием AI моделей.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import Base, engine, ensure_application_ready
from src.routers import api_router

# Проверка готовности приложения перед запуском
ensure_application_ready()

# Создание всех таблиц в базе данных на основе моделей
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI приложения
app = FastAPI(
    title="AudioScrobeAI",
    description="Backend для обработки аудиофайлов с использованием AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")


# Корневой эндпоинт
@app.get("/")
async def root() -> dict[str, str]:
    """
    Корневой эндпоинт приложения.

    Returns:
        dict: Приветственное сообщение.
    """
    return {"message": "Welcome to AudioScrobeAI API"}


# Эндпоинт для обратной совместимости
@app.get("/health")
async def legacy_health() -> dict[str, str]:
    """
    Устаревший эндпоинт здоровья для обратной совместимости.

    Рекомендуется использовать /api/v1/health/
    """
    return {
        "status": "ok",
        "message": "Используйте /api/v1/health/ для подробной информации",
    }
