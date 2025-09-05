"""
Модель аудиофайла.

Содержит информацию о загруженных аудиофайлах и их метаданные.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.models.enums import Status, StatusType

if TYPE_CHECKING:
    from src.models.users import User
    from src.models.transcriptions import Transcription

class AudioFile(Base):
    """
    Модель аудиофайла базы данных.

    Attributes:
        id: Уникальный идентификатор файла.
        user_id: ID пользователя-владельца (при удалении пользователя устанавливается в NULL).
        filename: Имя файла.
        filepath: Путь к файлу.
        format: Формат файла.
        size: Размер в байтах.
        duration: Длительность в секундах.
        add_time: Время добавления.
        status: Статус обработки.
        error_text: Текст ошибки (если есть).
        user: Связанный пользователь.
        transcriptions: Связанные транскрибации (удаляются каскадно при удалении файла).
    """
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # При удалении пользователя user_id устанавливается в NULL (каскадное правило SET NULL)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id', ondelete="SET NULL"), index=True, nullable=True)
    filename: Mapped[str] = mapped_column(String)
    original_filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    filepath: Mapped[str] = mapped_column(String)
    format: Mapped[str] = mapped_column(String)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in bytes
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in seconds
    add_time: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    # Use shared SQLAlchemy ENUM type from src.models.enums
    status: Mapped[Status] = mapped_column(StatusType)
    error_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="audio_files")
    transcriptions: Mapped[list["Transcription"]] = relationship(
        "Transcription",
        back_populates="audio_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
