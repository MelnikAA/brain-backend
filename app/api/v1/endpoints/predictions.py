from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
from pathlib import Path

from app.api import deps
from app.schemas.prediction import Prediction, PredictionCreate
from app.crud import crud_prediction
from app.services.ml_service import ml_service

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/", response_model=Prediction)
def create_prediction(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    Create new prediction.
    """
    # Сохраняем файл
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Делаем предсказание
    prediction_result, confidence = ml_service.predict(str(file_path))
    
    # Создаем запись в БД
    prediction_in = PredictionCreate(
        user_id=current_user.id,
        image_path=str(file_path),
        prediction_result=prediction_result,
        confidence=confidence
    )
    prediction = crud_prediction.create(db, obj_in=prediction_in)
    return prediction

@router.get("/", response_model=List[Prediction])
def read_predictions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve predictions.
    """
    predictions = crud_prediction.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return predictions 