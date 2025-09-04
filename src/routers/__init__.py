"""
Роутеры для API эндпоинтов.

Этот модуль содержит базовую конфигурацию роутеров для FastAPI приложения.
"""

from fastapi import APIRouter

# Создаем базовый роутер для группировки всех API роутеров
api_router = APIRouter()

# Импортируем и регистрируем все роутеры
from . import audio_files, auth, health, summaries, transcriptions, translations, users

# Включаем роутеры в основной API роутер
api_router.include_router(health.router, prefix="/health", tags=["health"])

api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(
    audio_files.router, prefix="/audio-files", tags=["audio-files"]
)

api_router.include_router(
    transcriptions.router, prefix="/transcriptions", tags=["transcriptions"]
)

api_router.include_router(
    translations.router, prefix="/translations", tags=["translations"]
)

api_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
