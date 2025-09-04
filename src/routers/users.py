"""
Роутер для эндпоинтов управления пользователями.

Этот модуль содержит эндпоинты для работы с пользователями системы:
получение списка пользователей, создание, обновление и удаление пользователей.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.users import User

# Создаем роутер для users эндпоинтов
router = APIRouter()


# Pydantic модели для API
class UserBase(BaseModel):
    """Базовая модель пользователя для API."""

    username: str
    is_admin: Optional[bool] = False

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Модель для создания пользователя."""

    password: str


class UserResponse(UserBase):
    """Модель ответа с пользователем."""

    id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[User]:
    """
    Получение списка всех пользователей.

    Args:
        skip: Количество пользователей для пропуска (пагинация).
        limit: Максимальное количество пользователей для возврата.
        db: Сессия базы данных.

    Returns:
        List[User]: Список пользователей.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    """
    Получение пользователя по ID.

    Args:
        user_id: ID пользователя.
        db: Сессия базы данных.

    Returns:
        User: Найденный пользователь.

    Raises:
        HTTPException: Если пользователь не найден.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Создание нового пользователя.

    Args:
        user: Данные для создания пользователя.
        db: Сессия базы данных.

    Returns:
        User: Созданный пользователь.

    Raises:
        HTTPException: Если пользователь с таким именем уже существует.
    """
    # Проверяем, существует ли пользователь с таким именем
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким именем уже существует"
        )

    # Создаем нового пользователя
    db_user = User(username=user.username, is_admin=user.is_admin)
    db_user.set_password(user.password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_update: UserBase, db: Session = Depends(get_db)
) -> User:
    """
    Обновление данных пользователя.

    Args:
        user_id: ID пользователя для обновления.
        user_update: Новые данные пользователя.
        db: Сессия базы данных.

    Returns:
        User: Обновленный пользователь.

    Raises:
        HTTPException: Если пользователь не найден.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем данные
    user.username = user_update.username
    if user_update.is_admin is not None:
        user.is_admin = user_update.is_admin

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Удаление пользователя.

    Args:
        user_id: ID пользователя для удаления.
        db: Сессия базы данных.

    Returns:
        dict: Сообщение об успешном удалении.

    Raises:
        HTTPException: Если пользователь не найден.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.delete(user)
    db.commit()

    return {"message": "Пользователь успешно удален"}
