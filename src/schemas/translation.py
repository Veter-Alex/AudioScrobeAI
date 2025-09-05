"""
Схемы для переводов (translation).

TranslationCreate — входная схема для создания перевода по транскрипции.
TranslationRead — схема вывода результатов перевода.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


from .common import ProcessingStatusLiteral


class TranslationCreate(BaseModel):
        """Схема входных данных для создания задачи перевода.

        Поля:
            transcription_id: id транскрипции, для которой нужен перевод.
            ai_model_id: id AI-модели, использующейся для перевода.
            text_translation_en/ru: переводные тексты (EN и RU).
            start_time, end_time: временные метки сегмента.
        """

        transcription_id: int
        ai_model_id: int
        text_translation_en: str
        text_translation_ru: str
        start_time: float = Field(..., ge=0.0)
        end_time: float = Field(..., ge=0.0)


class TranslationRead(BaseModel):
        """Схема вывода результата перевода.

        Поддерживает инициализацию из SQLAlchemy-объекта.
        """

        model_config = {"from_attributes": True}

        id: int
        transcription_id: int
        ai_model_id: int
        text_translation_en: str
        text_translation_ru: str
        start_time: float
        end_time: float
        status: ProcessingStatusLiteral
        error_text: Optional[str] = None
