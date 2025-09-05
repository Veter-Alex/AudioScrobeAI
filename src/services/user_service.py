"""
Сервис для операций с пользователями (бизнес-логика).

Содержит функции создания/обновления/удаления пользователей и простые
запросы к базе. Роутеры должны вызывать эти функции, а не содержать
логику работы с DB напрямую.
"""

from typing import Optional

from sqlalchemy.orm import Session

from src.models.users import User
from src.utils.security import hash_password


class UserService:
    @staticmethod
    def create_user(db: Session, username: str, password: str, is_admin: bool = False) -> User:
        """Создать пользователя, хэшируя пароль и сохранив запись в БД."""
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("user_exists")

        # create user via attribute assignment to satisfy SQLAlchemy mypy plugin
        user = User()
        user.username = username
        user.is_admin = is_admin
        user.password_hash = hash_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, username: str, is_admin: Optional[bool] = None) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise LookupError("not_found")
        user.username = username
        if is_admin is not None:
            user.is_admin = is_admin
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise LookupError("not_found")
        db.delete(user)
        db.commit()
