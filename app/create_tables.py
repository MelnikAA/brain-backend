import sys
from pathlib import Path
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.user import User
from app.models.prediction import Prediction
from app.models.image import Image
from app.models.patient import Patient

# Добавляем путь к корневой директории проекта
sys.path.append(str(Path(__file__).parent.parent))

def create_tables():
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    # Создаем таблицы в правильном порядке
    User.__table__.create(engine)  # Сначала создаем таблицу users
    Patient.__table__.create(engine)  # Затем создаем таблицу patients
    Image.__table__.create(engine)  # Затем создаем таблицу images
    Prediction.__table__.create(engine)  # И только потом создаем таблицу predictions
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    create_tables() 