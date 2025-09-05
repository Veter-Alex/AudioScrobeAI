"""Общие типы и литералы для схем.

Содержит общий ProcessingStatusLiteral, используемый в нескольких схемах.
"""

from typing import Literal


ProcessingStatusLiteral = Literal["pending", "in_progress", "completed", "failed"]
