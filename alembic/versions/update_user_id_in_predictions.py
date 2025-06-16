"""update user_id in predictions

Revision ID: update_user_id_in_predictions
Revises: add_updated_at_to_predictions
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_user_id_in_predictions'
down_revision = 'add_updated_at_to_predictions'
branch_labels = None
depends_on = None

def upgrade():
    # Получаем ID первого суперпользователя
    connection = op.get_bind()
    result = connection.execute("SELECT id FROM users WHERE is_superuser = true LIMIT 1")
    superuser_id = result.scalar()
    
    if superuser_id:
        # Обновляем все записи, где user_id is NULL
        op.execute(f"UPDATE predictions SET user_id = {superuser_id} WHERE user_id IS NULL")

def downgrade():
    # Не можем откатить это изменение, так как теряем информацию о владельце
    pass 