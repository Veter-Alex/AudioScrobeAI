"""Lazy exports for schemas to avoid importing heavy modules at package import time.

This module exposes schema symbols at the package level but performs
imports only when an attribute is accessed. This avoids circular imports
when other top-level modules import `src.schemas`.
"""

from typing import Any, TYPE_CHECKING


_EXPORTS = {
    "UserCreate": ("src.schemas.user", "UserCreate"),
    "UserRead": ("src.schemas.user", "UserRead"),
    "AudioFileCreate": ("src.schemas.audio_file", "AudioFileCreate"),
    "AudioFileRead": ("src.schemas.audio_file", "AudioFileRead"),
    "TranscriptionCreate": ("src.schemas.transcription", "TranscriptionCreate"),
    "TranscriptionRead": ("src.schemas.transcription", "TranscriptionRead"),
    "TranslationCreate": ("src.schemas.translation", "TranslationCreate"),
    "TranslationRead": ("src.schemas.translation", "TranslationRead"),
    "SummaryCreate": ("src.schemas.summary", "SummaryCreate"),
    "SummaryRead": ("src.schemas.summary", "SummaryRead"),
    "AIModelCreate": ("src.schemas.ai_model", "AIModelCreate"),
    "AIModelRead": ("src.schemas.ai_model", "AIModelRead"),
}

__all__ = (
    "UserCreate",
    "UserRead",
    "AudioFileCreate",
    "AudioFileRead",
    "TranscriptionCreate",
    "TranscriptionRead",
    "TranslationCreate",
    "TranslationRead",
    "SummaryCreate",
    "SummaryRead",
    "AIModelCreate",
    "AIModelRead",
)


if TYPE_CHECKING:
    # Expose names to static type checkers without importing modules at runtime
    from src.schemas.user import UserCreate, UserRead
    from src.schemas.audio_file import AudioFileCreate, AudioFileRead
    from src.schemas.transcription import TranscriptionCreate, TranscriptionRead
    from src.schemas.translation import TranslationCreate, TranslationRead
    from src.schemas.summary import SummaryCreate, SummaryRead
    from src.schemas.ai_model import AIModelCreate, AIModelRead


def __getattr__(name: str) -> Any:
    if name in _EXPORTS:
        module_name, attr = _EXPORTS[name]
        module = __import__(module_name, fromlist=[attr])
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return list(__all__)
