"""
Роутер для эндпоинтов аутентификации.

Этот модуль содержит эндпоинты для входа в систему и проверки токенов.
"""

import os
from datetime import datetime, timedelta
from typing import Dict

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.users import User

# Создаем роутер для auth эндпоинтов
router = APIRouter()

# Схема базовой аутентификации
security = HTTPBasic()

# Секретный ключ для JWT токенов
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey12345678901234567890123456789012")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Pydantic модели для API
class Token(BaseModel):
    """Модель токена доступа."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Модель данных токена."""

    username: str | None = None


class UserResponse(BaseModel):
    """Модель ответа с информацией о пользователе."""

    username: str
    is_admin: bool
    id: int

    class Config:
        from_attributes = True


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создает JWT токен доступа.

    Args:
        data: Данные для включения в токен.
        expires_delta: Время жизни токена.

    Returns:
        str: JWT токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Аутентифицирует пользователя.

    Args:
        db: Сессия базы данных.
        username: Имя пользователя.
        password: Пароль.

    Returns:
        User | None: Пользователь если аутентификация успешна, иначе None.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя из базовой аутентификации.

    Args:
        credentials: Учетные данные базовой аутентификации.
        db: Сессия базы данных.

    Returns:
        User: Текущий пользователь.

    Raises:
        HTTPException: Если аутентификация не удалась.
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)
) -> Token:
    """
    Получает токен доступа для пользователя.

    Args:
        credentials: Учетные данные пользователя.
        db: Сессия базы данных.

    Returns:
        Token: Токен доступа.

    Raises:
        HTTPException: Если аутентификация не удалась.
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Получает информацию о текущем пользователе.

    Args:
        current_user: Текущий аутентифицированный пользователь.

    Returns:
        User: Информация о пользователе.
    """
    return current_user


@router.post("/verify")
async def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Проверяет учетные данные пользователя.

    Args:
        credentials: Учетные данные для проверки.
        db: Сессия базы данных.

    Returns:
        Dict[str, str]: Результат проверки.

    Raises:
        HTTPException: Если аутентификация не удалась.
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )

    return {
        "message": "Аутентификация успешна",
        "username": user.username,
        "is_admin": str(user.is_admin),
    }
