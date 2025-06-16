from alembic.config import Config
from alembic import command
import os

# Создаем конфигурацию Alembic
alembic_cfg = Config("alembic.ini")

# Создаем новую миграцию
command.revision(alembic_cfg, 
                message="remove response column",
                autogenerate=True)

# Применяем миграцию
command.upgrade(alembic_cfg, "head") 