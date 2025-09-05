"""
Модель AI модели.

Содержит информацию о моделях искусственного интеллекта,
используемых для обработки аудио.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from src.database import Base

if TYPE_CHECKING:
    from src.models.transcriptions import Transcription
    from src.models.translations import Translation
    from src.models.summaries import Summary

class Operation(PyEnum):
    """Операции, поддерживаемые AI моделью.

    Каждая модель поддерживает ровно одну из этих операций.
    """
    transcription = "transcription"
    translation = "translation"
    summary = "summary"

class AIModel(Base):
    """
    Модель AI модели базы данных.

    Attributes:
        id: Уникальный идентификатор модели.
        model_name: Уникальное имя модели.
        model_path: Путь к модели.
        operations: Список поддерживаемых операций.
        transcriptions: Связанные транскрибации.
        translations: Связанные переводы.
        summaries: Связанные суммаризации.
    """
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String, unique=True, index=True)
    model_path: Mapped[str] = mapped_column(String)
    # Каждая модель поддерживает одну операцию — используем отдельный ENUM-столбец
    operation: Mapped[Operation] = mapped_column(SAEnum(Operation, name="operation", native_enum=True, create_type=False))

    # Relationships
    transcriptions: Mapped[list["Transcription"]] = relationship(
        "Transcription",
        back_populates="ai_model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    translations: Mapped[list["Translation"]] = relationship(
        "Translation",
        back_populates="ai_model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    summaries: Mapped[list["Summary"]] = relationship(
        "Summary",
        back_populates="ai_model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
