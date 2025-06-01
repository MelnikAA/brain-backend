from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate

class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    def create(self, db: Session, *, obj_in: PredictionCreate) -> Prediction:
        obj_in_data = obj_in.dict()
        db_obj = Prediction(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Prediction]:
        return (
            db.query(self.model)
            .filter(Prediction.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

crud_prediction = CRUDPrediction(Prediction) 