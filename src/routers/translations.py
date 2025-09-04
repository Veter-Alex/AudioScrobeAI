"""
Роутер для эндпоинтов работы с переводами.

Этот модуль содержит эндпоинты для создания, получения и управления переводами текста.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.enums import ProcessingStatus
from src.models.transcriptions import Transcription
from src.models.translations import Translation

# Создаем роутер для translations эндпоинтов
router = APIRouter()


# Pydantic модели для API
class TranslationBase(BaseModel):
    """Базовая модель перевода для API."""

    transcription_id: int
    target_language: str
    status: str = "pending"
    translated_text: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class TranslationResponse(TranslationBase):
    """Модель ответа с переводом."""

    id: int
    created_at: datetime
    updated_at: datetime


class TranslationCreate(BaseModel):
    """Модель для создания перевода."""

    transcription_id: int
    target_language: str


@router.get("/", response_model=List[TranslationResponse])
async def get_translations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    transcription_id: Optional[int] = None,
    target_language: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[Translation]:
    """
    Получение списка переводов.

    Args:
        skip: Количество записей для пропуска (пагинация).
        limit: Максимальное количество записей для возврата.
        status: Фильтр по статусу.
        transcription_id: Фильтр по ID транскрибации.
        target_language: Фильтр по целевому языку.
        db: Сессия базы данных.

    Returns:
        List[Translation]: Список переводов.
    """
    query = db.query(Translation)

    if status:
        query = query.filter(Translation.status == ProcessingStatus(status))

    if transcription_id:
        query = query.filter(Translation.transcription_id == transcription_id)

    if target_language:
        query = query.filter(Translation.target_language == target_language)

    translations = query.offset(skip).limit(limit).all()
    return translations


@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation(
    translation_id: int, db: Session = Depends(get_db)
) -> Translation:
    """
    Получение перевода по ID.

    Args:
        translation_id: ID перевода.
        db: Сессия базы данных.

    Returns:
        Translation: Найденный перевод.

    Raises:
        HTTPException: Если перевод не найден.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if translation is None:
        raise HTTPException(status_code=404, detail="Перевод не найден")
    return translation


@router.post("/", response_model=TranslationResponse)
async def create_translation(
    translation_data: TranslationCreate, db: Session = Depends(get_db)
) -> Translation:
    """
    Создание нового перевода.

    Args:
        translation_data: Данные для создания перевода.
        db: Сессия базы данных.

    Returns:
        Translation: Созданный перевод.

    Raises:
        HTTPException: Если транскрибация не найдена.
    """
    # Проверяем существование транскрибации
    transcription = (
        db.query(Transcription)
        .filter(Transcription.id == translation_data.transcription_id)
        .first()
    )
    if transcription is None:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")

    # Создаем перевод
    db_translation = Translation(
        transcription_id=translation_data.transcription_id,
        target_language=translation_data.target_language,
        status=ProcessingStatus.PENDING,
    )

    db.add(db_translation)
    db.commit()
    db.refresh(db_translation)

    return db_translation


@router.put("/{translation_id}", response_model=TranslationResponse)
async def update_translation(
    translation_id: int,
    translated_text: str,
    confidence: Optional[float] = None,
    db: Session = Depends(get_db),
) -> Translation:
    """
    Обновление текста перевода.

    Args:
        translation_id: ID перевода.
        translated_text: Переведенный текст.
        confidence: Уровень уверенности (опционально).
        db: Сессия базы данных.

    Returns:
        Translation: Обновленный перевод.

    Raises:
        HTTPException: Если перевод не найден.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if translation is None:
        raise HTTPException(status_code=404, detail="Перевод не найден")

    # Обновляем данные
    translation.translated_text = translated_text
    translation.status = ProcessingStatus.COMPLETED
    if confidence is not None:
        translation.confidence = confidence
    translation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(translation)

    return translation


@router.delete("/{translation_id}")
async def delete_translation(
    translation_id: int, db: Session = Depends(get_db)
) -> dict:
    """
    Удаление перевода.

    Args:
        translation_id: ID перевода для удаления.
        db: Сессия базы данных.

    Returns:
        dict: Сообщение об успешном удалении.

    Raises:
        HTTPException: Если перевод не найден.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if translation is None:
        raise HTTPException(status_code=404, detail="Перевод не найден")

    db.delete(translation)
    db.commit()

    return {"message": "Перевод успешно удален"}


@router.get("/stats/summary")
async def get_translation_stats(db: Session = Depends(get_db)) -> dict:
    """
    Получение статистики по переводам.

    Args:
        db: Сессия базы данных.

    Returns:
        dict: Статистика по переводам.
    """
    total_translations = db.query(Translation).count()

    # Статистика по статусам
    status_stats = db.query(Translation.status).all()
    status_counts: dict[str, int] = {}
    for status_tuple in status_stats:
        status = status_tuple[0]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Статистика по целевым языкам
    language_stats = db.query(Translation.target_language).all()
    language_counts: dict[str, int] = {}
    for lang_tuple in language_stats:
        lang = lang_tuple[0]
        language_counts[lang] = language_counts.get(lang, 0) + 1

    return {
        "total_translations": total_translations,
        "status_distribution": status_counts,
        "target_language_distribution": language_counts,
    }
