from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PredictionBase(BaseModel):
    image_path: str
    prediction_result: float
    confidence: float

class PredictionCreate(PredictionBase):
    user_id: int

class PredictionUpdate(PredictionBase):
    pass

class PredictionInDBBase(PredictionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Prediction(PredictionInDBBase):
    pass 