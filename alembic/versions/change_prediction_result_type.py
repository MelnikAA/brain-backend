"""change prediction result type to text

Revision ID: change_prediction_result_type
Revises: 
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'change_prediction_result_type'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Изменяем тип колонки на text
    op.alter_column('predictions', 'prediction_result',
                    existing_type=sa.Float(),
                    type_=sa.Text(),
                    existing_nullable=False)

def downgrade():
    # Возвращаем тип колонки на float
    op.alter_column('predictions', 'prediction_result',
                    existing_type=sa.Text(),
                    type_=sa.Float(),
                    existing_nullable=False) 