"""
Базовые Pydantic модели для схем (DTO).

Здесь определяются общие базовые классы и конфигурации, используемые
в остальных Pydantic схемах проекта. Модели настроены для работы
с объектами SQLAlchemy через from_attributes (Pydantic v2).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    """
    Базовая ORM-ориентированная модель Pydantic.

    Используется как базовый класс для схем, которые возвращают данные
   , полученные из SQLAlchemy-моделей. Включает конфигурацию
    `from_attributes=True`, чтобы Pydantic мог читать атрибуты
    объектов SQLAlchemy напрямую.
    """

    model_config = ConfigDict(from_attributes=True)
