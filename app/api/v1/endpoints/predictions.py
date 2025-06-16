from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from sqlalchemy.orm import Session, joinedload
import io
from PIL import Image
from pathlib import Path
import logging
import traceback
from datetime import datetime
from app.services import openrouter_service 
from app import crud
from app.api import deps
from app.core.config import settings
from app.schemas import prediction as schemas
from app.models.user import User

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

def is_valid_image(file: UploadFile) -> bool:
    """Проверяет, является ли файл валидным изображением"""
    try:
        # Проверяем расширение файла
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {ext}")
            return False
            
        # Проверяем content-type
        if not file.content_type or not file.content_type.startswith('image/'):
            logger.warning(f"Invalid content type: {file.content_type}")
            return False
            
        # Читаем весь файл
        contents = file.file.read()
        file.file.seek(0)  # Возвращаем указатель в начало файла
        
        # Пробуем открыть изображение
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Проверяем целостность файла
        return True
    except Exception as e:
        logger.error(f"Error validating image: {str(e)}")
        logger.error(traceback.format_exc())
        return False

@router.post("/", response_model=schemas.Prediction)
async def create_prediction(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    notes: str = Form(None),
    patient_id: int = Form(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new prediction using OpenRouter API.
    """
    logger.debug(f"Received prediction request for user {current_user.id}")
    
    # Проверяем формат файла
    if not is_valid_image(file):
        logger.warning(f"Invalid image format for user {current_user.id}")
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Пожалуйста, загрузите изображение в формате JPG или PNG."
        )

    # Проверяем количество попыток
   

    try:
        # Читаем содержимое файла
        logger.debug("Reading file contents")
        contents = await file.read()
        
        # Сохраняем изображение в базу данных
        logger.debug("Saving image to database")
        image = crud.crud_image.create_with_file(
            db=db,
            filename=file.filename,
            content_type=file.content_type,
            data=contents
        )
        logger.debug(f"Image saved with ID: {image.id}")
        from app.services.openrouter_service import openrouter_service

        # Создаем временный файл для анализа
        with io.BytesIO(contents) as buffer:
            # Делаем предсказание через OpenRouter API
            logger.debug("Sending image to OpenRouter API")
            results = openrouter_service.analyze_image(buffer)
            logger.debug(f"Received results from OpenRouter API: {results}")
            
            # Создаем запись в БД
            logger.debug("Creating prediction record")
            prediction_in = schemas.PredictionCreate(
                image_id=image.id,
                description=results["description"],
                conclusions=results["conclusions"],
                recommendations=results["recommendations"],
                confidence=results["confidence"],
                has_tumor=results["has_tumor"],
                medical_context=results["medical_context"],
                user_id=current_user.id,
                notes=notes,
                patient_id=patient_id
            )
            prediction = crud.prediction.create(db, obj_in=prediction_in)          
            logger.debug(f"Prediction record created with ID: {prediction.id}")
            
            # Уменьшаем количество попыток
           
            
            # Преобразуем объект в словарь и возвращаем его
            return {
                "id": prediction.id,
                "description": prediction.description,
                "conclusions": prediction.conclusions,
                "recommendations": prediction.recommendations,
                "notes": prediction.notes,
                "confidence": prediction.confidence,
                "has_tumor": prediction.has_tumor,
                "medical_context": prediction.medical_context,
                "segmentation_mask": prediction.segmentation_mask,
                "patient_id": prediction.patient_id,
                "image_id": prediction.image_id,
                "created_at": prediction.created_at,
                "user_id": prediction.user_id
            }
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Используйте формат YYYY-MM-DD"
        )

@router.get("/", response_model=schemas.PredictionList)
def read_predictions(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    has_tumor: Optional[bool] = Query(None),
    patient_id: Optional[int] = Query(None),
    owner_id: Optional[int] = Query(None),
    created_from: Optional[str] = Query(None, description="Фильтр по дате создания от (включительно) в формате YYYY-MM-DD"),
    created_to: Optional[str] = Query(None, description="Фильтр по дате создания до (включительно) в формате YYYY-MM-DD"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve predictions.
    For superusers - all predictions.
    For regular users - only their own predictions.
    """
    skip = (page - 1) * size

    query = db.query(crud.prediction.model).options(
        joinedload(crud.prediction.model.patient),
        joinedload(crud.prediction.model.owner)
    )

    # Фильтрация по параметрам
    if patient_id is not None:
        query = query.filter(crud.prediction.model.patient_id == patient_id)
    if has_tumor is not None:
        query = query.filter(crud.prediction.model.has_tumor == has_tumor)
    if owner_id is not None:
        query = query.filter(crud.prediction.model.user_id == owner_id)
    
    # Преобразуем строки дат в объекты datetime
    created_from_date = parse_date(created_from)
    created_to_date = parse_date(created_to)
    
    if created_from_date is not None:
        query = query.filter(crud.prediction.model.created_at >= created_from_date)
    if created_to_date is not None:
        # Устанавливаем время на конец дня для created_to
        created_to_date = datetime.combine(created_to_date.date(), datetime.max.time())
        query = query.filter(crud.prediction.model.created_at <= created_to_date)

    if current_user.is_superuser:
        predictions = query.order_by(crud.prediction.model.created_at.desc()).offset(skip).limit(size).all()
        total = query.count()
    else:
        query = query.filter(crud.prediction.model.user_id == current_user.id)
        predictions = query.order_by(crud.prediction.model.created_at.desc()).offset(skip).limit(size).all()
        total = query.count()

    pages = (total + size - 1) // size

    return {
        "items": predictions,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.get("/{id}", response_model=schemas.Prediction)
def read_prediction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get prediction by ID.
    For superusers - any prediction.
    For regular users - only their own predictions.
    """
    # Загружаем предсказание со связанными данными
    prediction = db.query(crud.prediction.model).options(
        joinedload(crud.prediction.model.patient),
        joinedload(crud.prediction.model.owner)
    ).filter(crud.prediction.model.id == id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if not current_user.is_superuser and prediction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return prediction 