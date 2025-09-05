"""
Простой пример сервиса для работы с аудиофайлами.

Этот модуль демонстрирует структуру и API сервиса. В реальном проекте
здесь содержалась бы логика сохранения/валидации/запусков задач AI и т.п.
"""

from typing import Optional

from sqlalchemy.orm import Session

from src.models.audio_files import AudioFile
from src.models.enums import Status


class AudioService:
    """Реализованный сервис для операций с аудиофайлами.

    Содержит бизнес-логику создания, удаления записи и получения статистики.
    """

    @staticmethod
    def create_audio_record(db: Session, filename: str, original_filename: str, file_size: int, user_id: Optional[int] = None, duration: Optional[float] = None, status: str = "uploaded") -> AudioFile:
        try:
            status_enum = Status(status)
        except Exception:
            status_enum = Status.UPLOADED

        db_audio_file = AudioFile()
        db_audio_file.filename = filename
        db_audio_file.original_filename = original_filename
        db_audio_file.file_size = file_size
        db_audio_file.duration = duration
        db_audio_file.status = status_enum
        db_audio_file.user_id = user_id
        db.add(db_audio_file)
        db.commit()
        db.refresh(db_audio_file)
        return db_audio_file

    @staticmethod
    def delete_audio_record(db: Session, file_id: int) -> None:
        audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
        if not audio_file:
            raise LookupError("not_found")
        db.delete(audio_file)
        db.commit()

    @staticmethod
    def get_stats(db: Session) -> dict:
        total_files = db.query(AudioFile).count()
        total_size = db.query(AudioFile).with_entities(AudioFile.file_size).all()
        total_size_bytes = sum(size[0] for size in total_size if size[0])
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
