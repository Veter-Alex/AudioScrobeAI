"""
Роутер для эндпоинтов проверки здоровья приложения.

Этот модуль содержит эндпоинты для мониторинга состояния приложения,
проверки здоровья базы данных и получения сводок о состоянии системы.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import ApplicationHealthChecker, get_db

# Создаем роутер для health эндпоинтов
router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Эндпоинт для комплексной проверки здоровья приложения.

    Выполняет полную проверку всех компонентов системы:
    - Переменные окружения
    - Подключение к базе данных
    - Наличие необходимых таблиц
    - Права доступа к БД
    - Корректность настроек приложения

    Returns:
        Dict[str, Any]: Подробный отчет о состоянии всех компонентов.
    """
    checker = ApplicationHealthChecker()
    health_result = checker.perform_full_health_check()

    return {
        "status": health_result["overall_status"],
        "timestamp": "2025-09-04T12:00:00Z",  # Можно заменить на datetime.utcnow().isoformat()
        "version": "1.0.0",
        "checks": health_result["checks"],
    }


@router.get("/summary")
async def health_summary() -> Dict[str, str]:
    """
    Эндпоинт для получения краткой сводки здоровья приложения.

    Returns:
        Dict[str, str]: Краткая сводка состояния приложения.
    """
    checker = ApplicationHealthChecker()
    summary = checker.get_health_summary()

    return {"summary": summary}


@router.get("/database")
async def database_health() -> Dict[str, Any]:
    """
    Эндпоинт для проверки здоровья базы данных.

    Returns:
        Dict[str, Any]: Состояние подключения и таблиц базы данных.
    """
    checker = ApplicationHealthChecker()

    return {
        "connection": checker.check_database_connection(),
        "tables": checker.check_database_tables(),
        "permissions": checker.check_database_permissions(),
    }


@router.get("/environment")
async def environment_health() -> Dict[str, Any]:
    """
    Эндпоинт для проверки переменных окружения.

    Returns:
        Dict[str, Any]: Состояние переменных окружения.
    """
    checker = ApplicationHealthChecker()
    return checker.check_environment_variables()


@router.get("/settings")
async def settings_health() -> Dict[str, Any]:
    """
    Эндпоинт для проверки настроек приложения.

    Returns:
        Dict[str, Any]: Состояние настроек приложения.
    """
    checker = ApplicationHealthChecker()
    return checker.check_application_settings()
