"""
Модель перевода.

Содержит результаты перевода транскрибаций.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.models.enums import ProcessingStatus, ProcessingStatusType

if TYPE_CHECKING:
    from src.models.transcriptions import Transcription
    from src.models.ai_models import AIModel

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

    # Relationships
    transcription: Mapped["Transcription"] = relationship("Transcription", back_populates="translations")
    ai_model: Mapped["AIModel"] = relationship("AIModel", back_populates="translations")
    summaries = relationship("Summary", back_populates="translation")
