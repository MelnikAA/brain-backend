from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.crud.base import CRUDBase
from app.models.image import Image
from app.schemas.image import ImageCreate

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CRUDImage(CRUDBase[Image, ImageCreate, ImageCreate]):
    def get(self, db: Session, id: int) -> Optional[Image]:
        """
        Получение изображения по ID
        """
        logger.debug(f"CRUD: Attempting to get image with ID: {id}")
        image = db.query(self.model).filter(self.model.id == id).first()
        logger.debug(f"CRUD: Image found: {image is not None}")
        if image:
            logger.debug(f"CRUD: Image data size: {len(image.data) if image.data else 0} bytes")
        return image

    def create_with_file(
        self,
        db: Session,
        *,
        filename: str,
        content_type: str,
        data: bytes
    ) -> Image:
        """
        Создание записи изображения с файлом
        """
        db_obj = Image(
            filename=filename,
            content_type=content_type,
            data=data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_image = CRUDImage(Image) 