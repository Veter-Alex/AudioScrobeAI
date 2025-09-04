"""
Роутер для эндпоинтов работы со сводками.

Этот модуль содержит эндпоинты для создания, получения и управления сводками текста.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.enums import ProcessingStatus
from src.models.summaries import Summary
from src.models.transcriptions import Transcription

# Создаем роутер для summaries эндпоинтов
router = APIRouter()


# Pydantic модели для API
class SummaryBase(BaseModel):
    """Базовая модель сводки для API."""

    transcription_id: int
    summary_type: str = "general"
    status: str = "pending"
    summary_text: Optional[str] = None
    key_points: Optional[List[str]] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class SummaryResponse(SummaryBase):
    """Модель ответа со сводкой."""

    id: int
    created_at: datetime
    updated_at: datetime


class SummaryCreate(BaseModel):
    """Модель для создания сводки."""

    transcription_id: int
    summary_type: str = "general"


@router.get("/", response_model=List[SummaryResponse])
async def get_summaries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    transcription_id: Optional[int] = None,
    summary_type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[Summary]:
    """
    Получение списка сводок.

    Args:
        skip: Количество записей для пропуска (пагинация).
        limit: Максимальное количество записей для возврата.
        status: Фильтр по статусу.
        transcription_id: Фильтр по ID транскрибации.
        summary_type: Фильтр по типу сводки.
        db: Сессия базы данных.

    Returns:
        List[Summary]: Список сводок.
    """
    query = db.query(Summary)

    if status:
        query = query.filter(Summary.status == ProcessingStatus(status))

    if transcription_id:
        query = query.filter(Summary.transcription_id == transcription_id)

    if summary_type:
        query = query.filter(Summary.summary_type == summary_type)

    summaries = query.offset(skip).limit(limit).all()
    return summaries


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(summary_id: int, db: Session = Depends(get_db)) -> Summary:
    """
    Получение сводки по ID.

    Args:
        summary_id: ID сводки.
        db: Сессия базы данных.

    Returns:
        Summary: Найденная сводка.

    Raises:
        HTTPException: Если сводка не найдена.
    """
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Сводка не найдена")
    return summary


@router.post("/", response_model=SummaryResponse)
async def create_summary(
    summary_data: SummaryCreate, db: Session = Depends(get_db)
) -> Summary:
    """
    Создание новой сводки.

    Args:
        summary_data: Данные для создания сводки.
        db: Сессия базы данных.

    Returns:
        Summary: Созданная сводка.

    Raises:
        HTTPException: Если транскрибация не найдена.
    """
    # Проверяем существование транскрибации
    transcription = (
        db.query(Transcription)
        .filter(Transcription.id == summary_data.transcription_id)
        .first()
    )
    if transcription is None:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")

    # Создаем сводку
    db_summary = Summary(
        transcription_id=summary_data.transcription_id,
        summary_type=summary_data.summary_type,
        status=ProcessingStatus.PENDING,
    )

    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)

    return db_summary


@router.put("/{summary_id}", response_model=SummaryResponse)
async def update_summary(
    summary_id: int,
    summary_text: str,
    key_points: Optional[List[str]] = None,
    confidence: Optional[float] = None,
    db: Session = Depends(get_db),
) -> Summary:
    """
    Обновление текста сводки.

    Args:
        summary_id: ID сводки.
        summary_text: Текст сводки.
        key_points: Ключевые моменты (опционально).
        confidence: Уровень уверенности (опционально).
        db: Сессия базы данных.

    Returns:
        Summary: Обновленная сводка.

    Raises:
        HTTPException: Если сводка не найдена.
    """
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Сводка не найдена")

    # Обновляем данные
    summary.summary_text = summary_text
    summary.status = ProcessingStatus.COMPLETED
    if key_points is not None:
        summary.key_points = key_points
    if confidence is not None:
        summary.confidence = confidence
    summary.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(summary)

    return summary


@router.delete("/{summary_id}")
async def delete_summary(summary_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Удаление сводки.

    Args:
        summary_id: ID сводки для удаления.
        db: Сессия базы данных.

    Returns:
        dict: Сообщение об успешном удалении.

    Raises:
        HTTPException: Если сводка не найдена.
    """
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Сводка не найдена")

    db.delete(summary)
    db.commit()

    return {"message": "Сводка успешно удалена"}


@router.get("/stats/summary")
async def get_summary_stats(db: Session = Depends(get_db)) -> dict:
    """
    Получение статистики по сводкам.

    Args:
        db: Сессия базы данных.

    Returns:
        dict: Статистика по сводкам.
    """
    total_summaries = db.query(Summary).count()

    # Статистика по статусам
    status_stats = db.query(Summary.status).all()
    status_counts: dict[str, int] = {}
    for status_tuple in status_stats:
        status = status_tuple[0]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Статистика по типам сводок
    type_stats = db.query(Summary.summary_type).all()
    type_counts: dict[str, int] = {}
    for type_tuple in type_stats:
        summary_type = type_tuple[0]
        type_counts[summary_type] = type_counts.get(summary_type, 0) + 1

    return {
        "total_summaries": total_summaries,
        "status_distribution": status_counts,
        "summary_type_distribution": type_counts,
    }
