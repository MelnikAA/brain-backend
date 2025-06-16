from app.db.session import SessionLocal
from sqlalchemy import text

def reset_alembic():
    db = SessionLocal()
    try:
        # Удаляем таблицу alembic_version
        db.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.commit()
        print("Таблица alembic_version успешно удалена")
    except Exception as e:
        print(f"Ошибка при удалении таблицы: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_alembic() 