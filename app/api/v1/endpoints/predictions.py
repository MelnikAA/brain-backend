from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
from pathlib import Path
from PIL import Image
import io

from app.api import deps
from app.schemas.prediction import Prediction, PredictionCreate
from app.crud.crud_prediction import crud_prediction
from app.crud.crud_user import crud_user
from app.services.openrouter_service import openrouter_service
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

def is_valid_image(file: UploadFile) -> bool:
    """Проверяет, является ли файл валидным изображением"""
    try:
        print(f"Проверка файла: {file.filename}")
        # Проверяем расширение файла
        ext = Path(file.filename).suffix.lower()
        print(f"Расширение файла: {ext}")
        if ext not in ALLOWED_EXTENSIONS:
            print(f"Неподдерживаемое расширение: {ext}")
            return False
            
        # Проверяем content-type
        if not file.content_type or not file.content_type.startswith('image/'):
            print(f"Неподдерживаемый content-type: {file.content_type}")
            return False
            
        # Читаем весь файл
        contents = file.file.read()
        file.file.seek(0)  # Возвращаем указатель в начало файла
        
        # Пробуем открыть изображение
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Проверяем целостность файла
        print("Файл успешно проверен")
        return True
    except Exception as e:
        print(f"Ошибка при проверке файла: {str(e)}")
        return False

@router.post("/", response_model=Prediction)
def create_prediction(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new prediction using OpenRouter API.
    """
    print(f"Получен файл: {file.filename}, content_type: {file.content_type}")
    
    # Проверяем формат файла
    if not is_valid_image(file):
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Пожалуйста, загрузите изображение в формате JPG или PNG. Получен файл: {file.filename}, content_type: {file.content_type}"
        )

    # Проверяем количество попыток
    if current_user.analysis_attempts <= 0:
        raise HTTPException(
            status_code=400,
            detail="У вас закончились попытки анализа. Пожалуйста, обратитесь к администратору."
        )

    # Сохраняем файл
    file_path = UPLOAD_DIR / file.filename
    try:
        # Сохраняем файл
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Делаем предсказание через OpenRouter API
        results = openrouter_service.analyze_image(str(file_path))
        
        # Создаем запись в БД
        prediction_in = PredictionCreate(
            image_path=str(file_path),
            prediction_result=results["prediction_result"],
            confidence=results["confidence"],
            user_id=current_user.id
        )
        prediction = crud_prediction.create(db, obj_in=prediction_in)
        
        # Уменьшаем количество попыток
        crud_user.decrement_analysis_attempts(db, user=current_user)
        
        return prediction
    except Exception as e:
        # В случае ошибки удаляем файл
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )

@router.get("/", response_model=List[Prediction])
def read_predictions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve predictions.
    """
    predictions = crud_prediction.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return predictions 