"""
Модуль с перечислениями (enums) для моделей.

Содержит определения статусов для различных процессов обработки.
"""

from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum

class Status(PyEnum):
    """Статусы загрузки аудиофайлов."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"

class ProcessingStatus(PyEnum):
    """Статусы обработки (транскрибация, перевод, суммаризация)."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# SQLAlchemy типы для PostgreSQL native ENUM
# create_type=False предотвращает повторное создание типа
StatusType = SAEnum(Status, name="status", native_enum=True, create_type=False)
ProcessingStatusType = SAEnum(ProcessingStatus, name="processing_status", native_enum=True, create_type=False)

__all__ = ["Status", "StatusType", "ProcessingStatus", "ProcessingStatusType"]
