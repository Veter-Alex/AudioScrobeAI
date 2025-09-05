"""
Модель транскрибации.

Содержит результаты транскрибации аудиофайлов.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.models.enums import ProcessingStatus, ProcessingStatusType

if TYPE_CHECKING:
    from src.models.audio_files import AudioFile
    from src.models.ai_models import AIModel
    from src.models.translations import Translation

class Transcription(Base):
    """
    Модель транскрибации базы данных.

    Attributes:
        id: Уникальный идентификатор транскрибации.
        audio_file_id: ID аудиофайла (удаляется каскадно при удалении файла).
        ai_model_id: ID AI модели.
        language: Язык транскрибации.
        text_transcription: Текст транскрибации.
        start_time: Время начала сегмента.
        end_time: Время окончания сегмента.
        status: Статус обработки.
        error_text: Текст ошибки (если есть).
        audio_file: Связанный аудиофайл.
        ai_model: Связанная AI модель.
        translations: Связанные переводы (удаляются каскадно при удалении транскрибации).
    """
    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # При удалении аудиофайла транскрибация удаляется каскадно
    audio_file_id: Mapped[int] = mapped_column(Integer, ForeignKey('audio_files.id', ondelete="CASCADE"), index=True)
    ai_model_id: Mapped[int] = mapped_column(Integer, ForeignKey('ai_models.id'), index=True)
    language: Mapped[str] = mapped_column(String)
    text_transcription: Mapped[str] = mapped_column(String)
    start_time: Mapped[float] = mapped_column(Float)  # in seconds
    end_time: Mapped[float] = mapped_column(Float)  # in seconds
    status: Mapped[ProcessingStatus] = mapped_column(ProcessingStatusType)
    error_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Timestamps and optional confidence
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    audio_file: Mapped["AudioFile"] = relationship("AudioFile", back_populates="transcriptions")
    ai_model: Mapped["AIModel"] = relationship("AIModel", back_populates="transcriptions")
    translations: Mapped[list["Translation"]] = relationship(
        "Translation",
        back_populates="transcription",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Compatibility property: allow router code to use .text
    @property
    def text(self) -> str:
        return self.text_transcription

    @text.setter
    def text(self, value: str) -> None:
        self.text_transcription = value
