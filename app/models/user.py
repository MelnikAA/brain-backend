from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    """
    Модель пользователя системы.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        email (str): Email пользователя (уникальный)
        hashed_password (str): Хешированный пароль
        full_name (str, optional): Полное имя пользователя
        is_active (bool): Флаг активности пользователя
        is_superuser (bool): Флаг суперпользователя
        password_set_token (str, optional): Токен для установки пароля
        password_set_token_expires (datetime, optional): Срок действия токена
        predictions (relationship): Связь с предсказаниями пользователя
        created_at (datetime): Дата создания пользователя
        updated_at (datetime): Дата последнего обновления пользователя
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    password_set_token = Column(String, nullable=True)
    password_set_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    predictions = relationship("Prediction", back_populates="owner") 