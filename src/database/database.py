"""
Модуль для настройки базы данных.

Этот модуль содержит конфигурацию подключения к PostgreSQL,
создание движка SQLAlchemy, сессий и базового класса для моделей.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# URL для подключения к базе данных PostgreSQL
# Использует переменные окружения для гибкости
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('POSTGRES_DB', 'audioscrobeai')}"

# Создание движка SQLAlchemy для подключения к БД
engine = create_engine(DATABASE_URL)

# Фабрика сессий для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Генератор для получения сессии базы данных.

    Используется как зависимость в FastAPI для автоматического
    управления сессиями.

    Yields:
        Session: Сессия базы данных.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
