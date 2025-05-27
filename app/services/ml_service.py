import sys
from pathlib import Path
import os
import shutil
from datetime import datetime

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from ml.model import BrainTumorModel

class MLService:
    def __init__(self):
        self.model = BrainTumorModel()
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def save_upload_file(self, file):
        """Сохраняет загруженный файл и возвращает путь к нему"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.upload_dir / f"{timestamp}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(file_path)

    def analyze_image(self, file):
        """Анализирует изображение с помощью обеих моделей"""
        # Сохраняем файл
        file_path = self.save_upload_file(file)
        
        try:
            # Получаем результаты анализа
            results = self.model.analyze_image(file_path)
            
            # Удаляем временный файл
            os.remove(file_path)
            
            return results
        except Exception as e:
            # В случае ошибки тоже удаляем файл
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

# Создаем экземпляр сервиса
ml_service = MLService() 