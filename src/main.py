"""
Основной модуль приложения AudioScrobeAI.

Этот модуль содержит FastAPI приложение для обработки аудиофайлов,
транскрибации, переводов и суммаризации с использованием AI моделей.
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from src.database import engine, get_db, Base
from src.models import User

# Создание всех таблиц в базе данных на основе моделей
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI приложения
app = FastAPI(
    title="AudioScrobeAI",
    description="Backend для обработки аудиофайлов с использованием AI",
    version="1.0.0"
)

@app.get("/")
async def root() -> dict[str, str]:
    """
    Корневой эндпоинт приложения.

    Returns:
        dict: Приветственное сообщение.
    """
    return {"message": "Welcome to AudioScrobeAI"}

@app.get("/health")
async def health() -> dict[str, str]:
    """
    Эндпоинт для проверки здоровья приложения.

    Returns:
        dict: Статус приложения.
    """
    return {"status": "ok"}

@app.get("/users")
async def get_users(db: Session = Depends(get_db)) -> List[User]:
    """
    Получение списка всех пользователей.

    Args:
        db: Сессия базы данных.

    Returns:
        List[User]: Список пользователей.
    """
    users = db.query(User).all()
    return users
