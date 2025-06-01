from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PredictionBase(BaseModel):
    prediction_result: str
    confidence: float
    segmentation_mask: Optional[str] = None

class PredictionCreate(PredictionBase):
    image_path: str
    user_id: int

class PredictionUpdate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    image_path: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 