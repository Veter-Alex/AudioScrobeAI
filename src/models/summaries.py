"""
Модель суммаризации.

Содержит результаты суммаризации переводов.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.models.enums import ProcessingStatus, ProcessingStatusType

if TYPE_CHECKING:
    from src.models.translations import Translation
    from src.models.ai_models import AIModel

class Summary(Base):
    """
    Модель суммаризации базы данных.

    Attributes:
        id: Уникальный идентификатор суммаризации.
        translation_id: ID перевода (удаляется каскадно при удалении перевода).
        ai_model_id: ID AI модели.
        text_summary_en: Текст суммаризации на английском.
        text_summary_ru: Текст суммаризации на русском.
        start_time: Время начала сегмента.
        end_time: Время окончания сегмента.
        status: Статус обработки.
        error_text: Текст ошибки (если есть).
        translation: Связанный перевод.
        ai_model: Связанная AI модель.
    """
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # При удалении перевода суммаризация удаляется каскадно
    translation_id: Mapped[int] = mapped_column(Integer, ForeignKey('translations.id', ondelete="CASCADE"), index=True)
    ai_model_id: Mapped[int] = mapped_column(Integer, ForeignKey('ai_models.id'), index=True)
    text_summary_en: Mapped[str] = mapped_column(String)
    text_summary_ru: Mapped[str] = mapped_column(String)
    start_time: Mapped[float] = mapped_column(Float)  # in seconds
    end_time: Mapped[float] = mapped_column(Float)  # in seconds
    status: Mapped[ProcessingStatus] = mapped_column(ProcessingStatusType)
    error_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    translation: Mapped["Translation"] = relationship("Translation", back_populates="summaries")
    ai_model: Mapped["AIModel"] = relationship("AIModel", back_populates="summaries")
