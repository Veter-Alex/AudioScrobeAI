"""
Схемы для сущности аудиофайла.

AudioFileCreate — входная схема при загрузке/создании записи о файле.
AudioFileRead — схема для отдачи данных пользователю; поддерживает
инициализацию из SQLAlchemy-моделей через from_attributes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


StatusLiteral = Literal["uploaded", "processing", "done", "error"]


class AudioFileCreate(BaseModel):
        """Схема входных данных для создания записи об аудиофайле.

        Поля:
            filename: имя файла (строка).
            filepath: путь к файлу на сервере.
            format: формат (например, "mp3", "wav").
            size: размер в байтах (>= 0).
            duration: длительность в секундах (>= 0.0).
            user_id: опциональный id пользователя-владельца.
        """

        filename: str
        filepath: str
        format: str
        size: int = Field(..., ge=0)
        duration: float = Field(..., ge=0.0)
        user_id: Optional[int] = None


class AudioFileRead(BaseModel):
        """Схема вывода данных аудиофайла.

        Используется для сериализации полей модели AudioFile при отдаче через API.
        """

        model_config = {"from_attributes": True}

        id: int
        user_id: Optional[int]
        filename: str
        filepath: str
        format: str
        size: int
        duration: float
        add_time: Optional[datetime]
        status: StatusLiteral
        error_text: Optional[str] = None
