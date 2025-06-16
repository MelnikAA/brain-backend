from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
import logging

from app.api import deps
from app.crud.crud_image import crud_image
from app.models.user import User

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=dict)
async def create_image(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Загрузка изображения в базу данных.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Файл должен быть изображением"
        )

    # Читаем содержимое файла
    contents = await file.read()
    
    # Сохраняем изображение в базу данных
    image = crud_image.create_with_file(
        db=db,
        filename=file.filename,
        content_type=file.content_type,
        data=contents
    )
    
    return {"id": image.id}

@router.get("/{image_id}/view")
def get_image(
    *,
    db: Session = Depends(deps.get_db),
    image_id: int,
) -> Any:
    """
    Получение изображения по ID без авторизации.
    """
    logger.debug(f"Attempting to get image with ID: {image_id}")
    
    image = crud_image.get(db=db, id=image_id)
    logger.debug(f"Image found: {image is not None}")
    
    if not image:
        logger.warning(f"Image with ID {image_id} not found")
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    logger.debug(f"Image content type: {image.content_type}")
    logger.debug(f"Image data size: {len(image.data) if image.data else 0} bytes")
    
    return Response(
        content=image.data,
        media_type=image.content_type
    ) 