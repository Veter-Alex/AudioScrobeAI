"""
Модель AI модели.

Содержит информацию о моделях искусственного интеллекта,
используемых для обработки аудио.
"""

from __future__ import annotations
from sqlalchemy import Integer, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List
from enum import Enum as PyEnum
from src.database import Base

class Operation(PyEnum):
    """Операции, поддерживаемые AI моделью."""
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
    # Use SQLAlchemy Enum (aliased to SAEnum) inside PostgreSQL ARRAY
    operations: Mapped[List[Operation]] = mapped_column(ARRAY(SAEnum(Operation, name="operation")))

    # Relationships
    transcriptions = relationship("Transcription", back_populates="ai_model")
    translations = relationship("Translation", back_populates="ai_model")
    summaries = relationship("Summary", back_populates="ai_model")
