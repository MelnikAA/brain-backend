import sys
from pathlib import Path

# Добавляем путь к корневой директории проекта
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import engine
from app.db.base_class import Base
from app.models.prediction import Prediction
from app.models.user import User

def create_tables():
    """Создает все таблицы в базе данных"""
    # Сначала создаем таблицу users
    User.__table__.create(engine)
    # Затем создаем таблицу predictions
    Prediction.__table__.create(engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    create_tables() 