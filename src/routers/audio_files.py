"""
Роутер для эндпоинтов работы с аудиофайлами.

Этот модуль содержит эндпоинты для загрузки, обработки и управления аудиофайлами.
"""

import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.audio_files import AudioFile
from src.models.enums import Status
from src.models.users import User

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

    # Создаем запись об аудиофайле
    db_audio_file = AudioFile(
        filename=file_data.filename,
        original_filename=file_data.original_filename,
        file_size=file_data.file_size,
        duration=file_data.duration,
        status=(
            Status(file_data.status)
            if hasattr(file_data, "status")
            else Status("uploaded")
        ),
        user_id=user_id,
    )

    db.add(db_audio_file)
    db.commit()
    db.refresh(db_audio_file)

    return db_audio_file


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

    # Удаляем файл с диска, если он существует
    if os.path.exists(audio_file.filename):
        os.remove(audio_file.filename)

    db.delete(audio_file)
    db.commit()

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
    total_files = db.query(AudioFile).count()
    total_size = db.query(AudioFile).with_entities(AudioFile.file_size).all()
    total_size_bytes = sum(size[0] for size in total_size if size[0])

    # Статистика по статусам
    status_stats = db.query(AudioFile.status, AudioFile.file_size).all()

    return {
        "total_files": total_files,
        "total_size_bytes": total_size_bytes,
        "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
        "status_distribution": {
            status: len([f for f, _ in status_stats if f == status])
            for status in set(s[0] for s in status_stats)
        },
    }
