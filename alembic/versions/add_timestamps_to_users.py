"""add timestamps to users

Revision ID: add_timestamps_to_users
Revises: 
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'add_timestamps_to_users'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем столбцы created_at и updated_at
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    # Удаляем столбцы created_at и updated_at
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at') 