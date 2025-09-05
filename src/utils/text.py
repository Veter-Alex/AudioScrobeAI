"""
Утилиты для работы с текстом.

Простейшая функция `truncate` — обрезает строку до заданной длины
и добавляет многоточие, если было усечение.
"""

from typing import Optional


def truncate(text: Optional[str], length: int = 100) -> str:
    """Обрезать `text` до `length` символов, добавив '...' при усечении.

    Возвращает пустую строку, если входной `text` равен None.
    """

    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[: max(0, length - 3)] + "..."
