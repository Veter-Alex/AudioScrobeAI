"""
Модель пользователя.

Содержит информацию о пользователях системы, включая аутентификацию.
"""

from __future__ import annotations


from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.database import Base

if TYPE_CHECKING:
    from src.models.audio_files import AudioFile


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
    # DB uses ON DELETE SET NULL for audio_files.user_id, let DB handle deletes
    audio_files: Mapped[list["AudioFile"]] = relationship(
        "AudioFile", back_populates="user", passive_deletes=True
    )

    def set_password(self, password: str) -> None:
        """
        Устанавливает пароль, хэшируя его.

        Args:
            password: Пароль в открытом виде.
        """
        from src.utils.security import hash_password

        self.password_hash = hash_password(password)

    def verify_password(self, password: str) -> bool:
        """
        Проверяет пароль.

        Args:
            password: Пароль для проверки.

        Returns:
            bool: True если пароль верный.
        """
        from src.utils.security import verify_password

        return verify_password(password, self.password_hash)
