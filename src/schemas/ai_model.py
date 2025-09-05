"""
Схемы описания AI-моделей, используемых для транскрипции/перевода/сводок.

AIModelCreate — входная схема для регистрации новой модели.
AIModelRead — схема для вывода метаданных модели.
"""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


OperationLiteral = Literal["transcription", "translation", "summary"]


class AIModelCreate(BaseModel):
        """Схема регистрации AI-модели.

        Поля:
            model_name: человекочитаемое имя модели.
            model_path: путь (или идентификатор) к ресурсу модели.
            operations: список поддерживаемых операций (непустой).
        """

        model_name: str
        model_path: str
        operations: List[OperationLiteral] = Field(..., min_length=1)


class AIModelRead(BaseModel):
        """Схема вывода метаданных AI-модели.

        Поддерживает инициализацию из SQLAlchemy-объекта.
        """

        model_config = {"from_attributes": True}

        id: int
        model_name: str
        model_path: str
        operations: List[OperationLiteral]
