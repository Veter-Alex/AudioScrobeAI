"""
Схемы для транскрипций аудио.

TranscriptionCreate — входная схема для создания задачи транскрипции.
TranscriptionRead — схема вывода данных транскрипции (из модели).
"""

from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel, Field


ProcessingStatusLiteral = Literal["pending", "in_progress", "completed", "failed"]


class TranscriptionCreate(BaseModel):
        """Схема входных данных для создания транскрипции.

        Поля:
            audio_file_id: id связанного аудиофайла.
            ai_model_id: id AI-модели, используемой для транскрипции.
            language: ISO-код языка (минимум 2 символа).
            start_time, end_time: границы сегмента в секундах (>= 0.0).
        """

        audio_file_id: int
        ai_model_id: int
        language: str = Field(..., min_length=2)
        start_time: float = Field(..., ge=0.0)
        end_time: float = Field(..., ge=0.0)


class TranscriptionRead(BaseModel):
        """Схема вывода транскрипции.

        Поддерживает иерархическую инициализацию из объекта SQLAlchemy
        (через `model_config = {"from_attributes": True}`).
        """

        model_config = {"from_attributes": True}

        id: int
        audio_file_id: int
        ai_model_id: int
        language: str
        text_transcription: str
        start_time: float
        end_time: float
        status: ProcessingStatusLiteral
        error_text: Optional[str] = None
