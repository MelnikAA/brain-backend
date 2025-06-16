from alembic.config import Config
from alembic import command
import os

# Получаем путь к текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем конфигурацию Alembic
alembic_cfg = Config(os.path.join(current_dir, "alembic.ini"))

# Выполняем миграцию до последней версии
command.upgrade(alembic_cfg, "head") 