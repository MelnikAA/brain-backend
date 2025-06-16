from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database():
    # Создаем подключение к базе данных
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as connection:
        # Проверяем тип колонки response
        result = connection.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
        """))
        
        column_info = result.fetchone()
        if column_info:
            logger.info(f"Current column type: {column_info[1]}")
            
            # Если тип не json или jsonb, меняем его
            if column_info[1] not in ['json', 'jsonb']:
                logger.info("Changing column type to jsonb...")
                connection.execute(text("""
                    ALTER TABLE predictions 
                    ALTER COLUMN response TYPE jsonb 
                    USING response::jsonb;
                """))
                logger.info("Column type changed successfully")
            else:
                logger.info("Column type is already correct")
        
        # Очищаем таблицу predictions
        logger.info("Clearing predictions table...")
        connection.execute(text("DELETE FROM predictions;"))
        logger.info("Table cleared successfully")
        
        # Применяем изменения
        connection.commit()

if __name__ == "__main__":
    fix_database() 