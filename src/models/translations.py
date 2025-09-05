"""
Модель перевода.

Содержит результаты перевода транскрибаций.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.models.enums import ProcessingStatus, ProcessingStatusType

if TYPE_CHECKING:
    from src.models.transcriptions import Transcription
    from src.models.ai_models import AIModel
    from src.models.summaries import Summary

class Translation(Base):
    """
    Модель перевода базы данных.

    Attributes:
        id: Уникальный идентификатор перевода.
        transcription_id: ID транскрибации (удаляется каскадно при удалении транскрибации).
        ai_model_id: ID AI модели.
        text_translation_en: Текст перевода на английский.
        text_translation_ru: Текст перевода на русский.
        start_time: Время начала сегмента.
        end_time: Время окончания сегмента.
        status: Статус обработки.
        error_text: Текст ошибки (если есть).
        transcription: Связанная транскрибация.
        ai_model: Связанная AI модель.
        summaries: Связанные суммаризации (удаляются каскадно при удалении перевода).
    """
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # При удалении транскрибации перевод удаляется каскадно
    transcription_id: Mapped[int] = mapped_column(Integer, ForeignKey('transcriptions.id', ondelete="CASCADE"), index=True)
    ai_model_id: Mapped[int] = mapped_column(Integer, ForeignKey('ai_models.id'), index=True)
    text_translation_en: Mapped[str] = mapped_column(String)
    text_translation_ru: Mapped[str] = mapped_column(String)
    start_time: Mapped[float] = mapped_column(Float)  # in seconds
    end_time: Mapped[float] = mapped_column(Float)  # in seconds
    status: Mapped[ProcessingStatus] = mapped_column(ProcessingStatusType)
    error_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Timestamps and optional confidence and translated text fields
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Note: do not provide convenience properties for translated_text/target_language here.
    # Use explicit columns `text_translation_en`/`text_translation_ru` and a transient
    # attribute `_requested_target_language` when needed at runtime.

    # Relationships
    transcription: Mapped["Transcription"] = relationship(
        "Transcription",
        back_populates="translations",
    )
    ai_model: Mapped["AIModel"] = relationship(
        "AIModel",
        back_populates="translations",
    )
    summaries: Mapped[list["Summary"]] = relationship(
        "Summary",
        back_populates="translation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # no additional compatibility properties
