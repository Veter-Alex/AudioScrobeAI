"""
Безопасные утилиты: хеширование и проверка паролей.

Оборачиваем конкретную реализацию (passlib) чтобы не разводить вызовы
bcrypt по модели/сервисам напрямую.
"""

from passlib.hash import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return bool(bcrypt.verify(password, password_hash))
