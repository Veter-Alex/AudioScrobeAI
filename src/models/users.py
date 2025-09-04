"""
Модель пользователя.

Содержит информацию о пользователях системы, включая аутентификацию.
"""

from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class User(Base):
    """
    Модель пользователя базы данных.

    Attributes:
        id: Уникальный идентификатор пользователя.
        username: Уникальное имя пользователя.
        password_hash: Хэшированный пароль.
        is_admin: Флаг администратора.
        audio_files: Связанные аудиофайлы (обратная связь).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    # Указывает, имеет ли пользователь права администратора
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    audio_files = relationship("AudioFile", back_populates="user")

    def set_password(self, password: str) -> None:
        """
        Устанавливает пароль, хэшируя его.

        Args:
            password: Пароль в открытом виде.
        """
        from passlib.hash import bcrypt

        self.password_hash = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Проверяет пароль.

        Args:
            password: Пароль для проверки.

        Returns:
            bool: True если пароль верный.
        """
        from passlib.hash import bcrypt

        return bool(bcrypt.verify(password, self.password_hash))
