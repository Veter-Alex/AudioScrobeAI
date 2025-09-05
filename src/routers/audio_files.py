"""
Роутер для эндпоинтов работы с аудиофайлами.

Этот модуль содержит эндпоинты для загрузки, обработки и управления аудиофайлами.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.audio_files import AudioFile
from src.models.users import User
from src.services.audio_service import AudioService
from src.utils.fs import safe_remove

# Создаем роутер для audio files эндпоинтов
router = APIRouter()


# Pydantic модели для API
class AudioFileBase(BaseModel):
    """Базовая модель аудиофайла для API."""

    filename: str
    original_filename: str
    file_size: int
    duration: Optional[float] = None
    status: str = "uploaded"

    class Config:
        from_attributes = True


class AudioFileResponse(AudioFileBase):
    """Модель ответа с аудиофайлом."""

    id: int
    user_id: int
    upload_date: datetime


class AudioFileCreate(BaseModel):
    """Модель для создания аудиофайла."""

    filename: str
    original_filename: str
    file_size: int
    duration: Optional[float] = None
    status: str = "uploaded"


@router.get("/", response_model=List[AudioFileResponse])
async def get_audio_files(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[AudioFile]:
    """
    Получение списка аудиофайлов.

    Args:
        skip: Количество файлов для пропуска (пагинация).
        limit: Максимальное количество файлов для возврата.
        user_id: Фильтр по ID пользователя.
        db: Сессия базы данных.

    Returns:
        List[AudioFile]: Список аудиофайлов.
    """
    query = db.query(AudioFile)

    if user_id:
        query = query.filter(AudioFile.user_id == user_id)

    audio_files = query.offset(skip).limit(limit).all()
    return audio_files


@router.get("/{file_id}", response_model=AudioFileResponse)
async def get_audio_file(file_id: int, db: Session = Depends(get_db)) -> AudioFile:
    """
    Получение аудиофайла по ID.

    Args:
        file_id: ID аудиофайла.
        db: Сессия базы данных.

    Returns:
        AudioFile: Найденный аудиофайл.

    Raises:
        HTTPException: Если файл не найден.
    """
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if audio_file is None:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")
    return audio_file


@router.post("/", response_model=AudioFileResponse)
async def create_audio_file(
    file_data: AudioFileCreate, user_id: int, db: Session = Depends(get_db)
) -> AudioFile:
    """
    Создание записи об аудиофайле.

    Args:
        file_data: Данные аудиофайла.
        user_id: ID пользователя-владельца.
        db: Сессия базы данных.

    Returns:
        AudioFile: Созданная запись аудиофайла.

    Raises:
        HTTPException: Если пользователь не найден.
    """
    # Проверяем существование пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    created = AudioService.create_audio_record(
        db,
        filename=file_data.filename,
        original_filename=file_data.original_filename,
        file_size=file_data.file_size,
        duration=file_data.duration,
        user_id=user_id,
        status=file_data.status,
    )
    return created


@router.delete("/{file_id}")
async def delete_audio_file(file_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Удаление аудиофайла.

    Args:
        file_id: ID аудиофайла для удаления.
        db: Сессия базы данных.

    Returns:
        dict: Сообщение об успешном удалении.

    Raises:
        HTTPException: Если файл не найден.
    """
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if audio_file is None:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")

    # Удаляем файл с диска безопасно и удаляем запись
    try:
        safe_remove(audio_file.filename)
    except Exception:
        # не прерываем удаление записи, логирование можно добавить
        pass
    AudioService.delete_audio_record(db, file_id=file_id)
    return {"message": "Аудиофайл успешно удален"}


@router.get("/stats/summary")
async def get_audio_stats(db: Session = Depends(get_db)) -> dict:
    """
    Получение статистики по аудиофайлам.

    Args:
        db: Сессия базы данных.

    Returns:
        dict: Статистика по аудиофайлам.
    """
    return AudioService.get_stats(db)
