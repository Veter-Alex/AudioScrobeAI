"""
Схемы описания AI-моделей, используемых для транскрипции/перевода/сводок.

AIModelCreate — входная схема для регистрации новой модели.
AIModelRead — схема для вывода метаданных модели.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


OperationLiteral = Literal["transcription", "translation", "summary"]


class AIModelCreate(BaseModel):
        """Схема регистрации AI-модели.

        Поля:
                model_name: человекочитаемое имя модели.
                model_path: путь (или идентификатор) к ресурсу модели.
                operation: единственная поддерживаемая операция модели —
                        либо "transcription", либо "translation", либо "summary".
        """

        model_name: str
        model_path: str
        operation: OperationLiteral


class AIModelRead(BaseModel):
        """Схема вывода метаданных AI-модели.

        Поддерживает инициализацию из SQLAlchemy-объекта.
        """

        model_config = {"from_attributes": True}

        id: int
        model_name: str
        model_path: str
        operation: OperationLiteral
