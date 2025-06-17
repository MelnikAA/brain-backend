from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import desc, and_

from app.crud.base import CRUDBase
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate

class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    def create(self, db: Session, *, obj_in: PredictionCreate) -> Prediction:
        db_obj = Prediction(
            image_id=obj_in.image_id,
            description=obj_in.description,
            conclusions=obj_in.conclusions,
            recommendations=obj_in.recommendations,
            confidence=obj_in.confidence,
            has_tumor=obj_in.has_tumor,
            medical_context=obj_in.medical_context,
            segmentation_mask=obj_in.segmentation_mask,
            patient_id=obj_in.patient_id,
            user_id=obj_in.user_id,
            notes=obj_in.notes,
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        has_tumor: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        patient_id: Optional[int] = None
    ) -> List[Prediction]:
        query = db.query(Prediction)
        
        if has_tumor is not None:
            query = query.filter(Prediction.has_tumor == has_tumor)
        if created_from:
            query = query.filter(Prediction.created_at >= created_from)
        if created_to:
            query = query.filter(Prediction.created_at <= created_to)
        if patient_id:
            query = query.filter(Prediction.patient_id == patient_id)
            
        return query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()

    def count(
        self,
        db: Session,
        *,
        has_tumor: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        patient_id: Optional[int] = None
    ) -> int:
        query = db.query(Prediction)
        
        if has_tumor is not None:
            query = query.filter(Prediction.has_tumor == has_tumor)
        if created_from:
            query = query.filter(Prediction.created_at >= created_from)
        if created_to:
            query = query.filter(Prediction.created_at <= created_to)
        if patient_id:
            query = query.filter(Prediction.patient_id == patient_id)
            
        return query.count()

    def count_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        has_tumor: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        patient_id: Optional[int] = None
    ) -> int:
        query = db.query(Prediction).filter(Prediction.user_id == user_id)
        
        if has_tumor is not None:
            query = query.filter(Prediction.has_tumor == has_tumor)
        if created_from:
            query = query.filter(Prediction.created_at >= created_from)
        if created_to:
            query = query.filter(Prediction.created_at <= created_to)
        if patient_id:
            query = query.filter(Prediction.patient_id == patient_id)
            
        return query.count()

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        has_tumor: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        patient_id: Optional[int] = None
    ) -> List[Prediction]:
        query = db.query(Prediction).filter(Prediction.user_id == user_id)
        
        if has_tumor is not None:
            query = query.filter(Prediction.has_tumor == has_tumor)
        if created_from:
            query = query.filter(Prediction.created_at >= created_from)
        if created_to:
            query = query.filter(Prediction.created_at <= created_to)
        if patient_id:
            query = query.filter(Prediction.patient_id == patient_id)
            
        return query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()

prediction = CRUDPrediction(Prediction) 