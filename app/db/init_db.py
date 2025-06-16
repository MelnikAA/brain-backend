from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine

def init_db() -> None:
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine) 