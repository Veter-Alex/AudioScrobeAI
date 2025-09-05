"""
Утилиты для работы с файловой системой.

safe_remove(path) — безопасно удаляет файл, если он существует.
"""

import os
from typing import Optional


def safe_remove(path: Optional[str]) -> None:
    """Удаляет файл по пути `path`, если он существует.

    Ничего не делает, если путь пустой или файла нет.
    """

    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        # логирование можно добавить здесь
        pass
