"""
Схемы Pydantic для работы с пользователями.

UserCreate — схема для создания пользователя (входные данные).
UserRead — схема для чтения пользователя (выходные данные),
поддерживает загрузку полей из SQLAlchemy-объекта (from_attributes).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Схема входных данных для создания пользователя.

    Поля:
        username: логин пользователя, минимум 3 символа, максимум 150.
        password: пароль (в открытом виде) минимум 8 символов.
    """

    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=8)


class UserRead(BaseModel):
    """Схема для вывода данных пользователя.

    Используется при возвращении пользователей из API. `model_config`
    позволяет создавать экземпляр схемы из SQLAlchemy-объекта.
    """

    model_config = {"from_attributes": True}

    id: int
    username: str
    is_admin: bool = False
