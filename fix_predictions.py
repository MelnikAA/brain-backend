from app.db.session import SessionLocal
from sqlalchemy import text
from datetime import datetime

def fix_predictions():
    db = SessionLocal()
    try:
        # Проверяем количество NULL значений
        result = db.execute(text("SELECT COUNT(*) FROM predictions WHERE created_at IS NULL"))
        null_count = result.scalar()
        print(f"Найдено {null_count} записей с NULL в created_at")

        if null_count > 0:
            # Обновляем NULL значения в created_at
            db.execute(
                text("""
                    UPDATE predictions 
                    SET created_at = CURRENT_TIMESTAMP 
                    WHERE created_at IS NULL
                """)
            )
            db.commit()
            print("NULL значения в created_at успешно обновлены")
        else:
            print("Нет записей с NULL в created_at")

    except Exception as e:
        print(f"Ошибка при обновлении данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_predictions() 