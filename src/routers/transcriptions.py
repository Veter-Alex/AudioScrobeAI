"""
Роутер для эндпоинтов работы с транскрибациями.

Этот модуль содержит эндпоинты для создания, получения и управления транскрибациями аудиофайлов.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.audio_files import AudioFile
from src.models.enums import ProcessingStatus
from src.models.transcriptions import Transcription

# Создаем роутер для transcriptions эндпоинтов
router = APIRouter()


# Pydantic модели для API
class TranscriptionBase(BaseModel):
    """Базовая модель транскрибации для API."""

    audio_file_id: int
    language: str = "auto"
    status: str = "pending"
    text: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class TranscriptionResponse(TranscriptionBase):
    """Модель ответа с транскрибацией."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TranscriptionCreate(BaseModel):
    """Модель для создания транскрибации."""

    audio_file_id: int
    language: str = "auto"


@router.get("/", response_model=List[TranscriptionResponse])
async def get_transcriptions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    audio_file_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[Transcription]:
    """
    Получение списка транскрибаций.

    Args:
        skip: Количество записей для пропуска (пагинация).
        limit: Максимальное количество записей для возврата.
        status: Фильтр по статусу.
        audio_file_id: Фильтр по ID аудиофайла.
        db: Сессия базы данных.

    Returns:
        List[Transcription]: Список транскрибаций.
    """
    query = db.query(Transcription)

    if status:
        query = query.filter(Transcription.status == ProcessingStatus(status))

    if audio_file_id:
        query = query.filter(Transcription.audio_file_id == audio_file_id)

    transcriptions = query.offset(skip).limit(limit).all()
    return transcriptions


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: int, db: Session = Depends(get_db)
) -> Transcription:
    """
    Получение транскрибации по ID.

    Args:
        transcription_id: ID транскрибации.
        db: Сессия базы данных.

    Returns:
        Transcription: Найденная транскрибация.

    Raises:
        HTTPException: Если транскрибация не найдена.
    """
    transcription = (
        db.query(Transcription).filter(Transcription.id == transcription_id).first()
    )
    if transcription is None:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")
    return transcription


@router.post("/", response_model=TranscriptionResponse)
async def create_transcription(
    transcription_data: TranscriptionCreate, db: Session = Depends(get_db)
) -> Transcription:
    """
    Создание новой транскрибации.

    Args:
        transcription_data: Данные для создания транскрибации.
        db: Сессия базы данных.

    Returns:
        Transcription: Созданная транскрибация.

    Raises:
        HTTPException: Если аудиофайл не найден.
    """
    # Проверяем существование аудиофайла
    audio_file = (
        db.query(AudioFile)
        .filter(AudioFile.id == transcription_data.audio_file_id)
        .first()
    )
    if audio_file is None:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")

    # Создаем транскрибацию
    db_transcription = Transcription(
        audio_file_id=transcription_data.audio_file_id,
        language=transcription_data.language,
        status=ProcessingStatus.PENDING,
    )

    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)

    return db_transcription


@router.put("/{transcription_id}", response_model=TranscriptionResponse)
async def update_transcription(
    transcription_id: int,
    text: str,
    confidence: Optional[float] = None,
    db: Session = Depends(get_db),
) -> Transcription:
    """
    Обновление текста транскрибации.

    Args:
        transcription_id: ID транскрибации.
        text: Текст транскрибации.
        confidence: Уровень уверенности (опционально).
        db: Сессия базы данных.

    Returns:
        Transcription: Обновленная транскрибация.

    Raises:
        HTTPException: Если транскрибация не найдена.
    """
    transcription = (
        db.query(Transcription).filter(Transcription.id == transcription_id).first()
    )
    if transcription is None:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")

    # Обновляем данные
    transcription.text = text
    transcription.status = ProcessingStatus.COMPLETED
    if confidence is not None:
        transcription.confidence = confidence
    transcription.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(transcription)

    return transcription


@router.delete("/{transcription_id}")
async def delete_transcription(
    transcription_id: int, db: Session = Depends(get_db)
) -> dict:
    """
    Удаление транскрибации.

    Args:
        transcription_id: ID транскрибации для удаления.
        db: Сессия базы данных.

    Returns:
        dict: Сообщение об успешном удалении.

    Raises:
        HTTPException: Если транскрибация не найдена.
    """
    transcription = (
        db.query(Transcription).filter(Transcription.id == transcription_id).first()
    )
    if transcription is None:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")

    db.delete(transcription)
    db.commit()

    return {"message": "Транскрибация успешно удалена"}


@router.get("/stats/summary")
async def get_transcription_stats(db: Session = Depends(get_db)) -> dict:
    """
    Получение статистики по транскрибациям.

    Args:
        db: Сессия базы данных.

    Returns:
        dict: Статистика по транскрибациям.
    """
    total_transcriptions = db.query(Transcription).count()

    # Статистика по статусам
    status_stats = db.query(Transcription.status).all()
    status_counts: dict[str, int] = {}
    for status_tuple in status_stats:
        status = status_tuple[0]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Статистика по языкам
    language_stats = db.query(Transcription.language).all()
    language_counts: dict[str, int] = {}
    for lang_tuple in language_stats:
        lang = lang_tuple[0]
        language_counts[lang] = language_counts.get(lang, 0) + 1

    return {
        "total_transcriptions": total_transcriptions,
        "status_distribution": status_counts,
        "language_distribution": language_counts,
    }
