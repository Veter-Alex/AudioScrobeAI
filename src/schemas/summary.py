"""
Схемы для кратких сводок (summaries).

SummaryCreate — входная схема для генерации сводки на базе перевода.
SummaryRead — схема для отдачи результата.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


from .common import ProcessingStatusLiteral


class SummaryCreate(BaseModel):
        """Схема входных данных для создания задачи по генерации сводки.

        Поля:
            translation_id: id перевода, используемого как источник.
            ai_model_id: id модели AI для генерации сводки.
            text_summary_en/ru: итоговые тексты на EN и RU (при завершении).
            start_time, end_time: временные метки сегмента.
        """

        translation_id: int
        ai_model_id: int
        text_summary_en: str
        text_summary_ru: str
        start_time: float = Field(..., ge=0.0)
        end_time: float = Field(..., ge=0.0)


class SummaryRead(BaseModel):
        """Схема вывода результата сводки.

        Поддерживает загрузку значений из SQLAlchemy-объекта.
        """

        model_config = {"from_attributes": True}

        id: int
        translation_id: int
        ai_model_id: int
        text_summary_en: str
        text_summary_ru: str
        start_time: float
        end_time: float
        status: ProcessingStatusLiteral
        error_text: Optional[str] = None
