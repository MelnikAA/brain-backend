from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PatientInfo(BaseModel):
    id: int
    full_name: str
    birth_date: datetime

    model_config = ConfigDict(from_attributes=True)

class DoctorInfo(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class PredictionBase(BaseModel):
    image_id: int
    description: str
    conclusions: str
    recommendations: str
    notes: Optional[str] = None
    confidence: float
    has_tumor: bool
    medical_context: str
    segmentation_mask: Optional[str] = None
    patient_id: Optional[int] = None

class PredictionCreate(PredictionBase):
    user_id: int

class PredictionUpdate(PredictionBase):
    image_id: Optional[int] = None
    description: Optional[str] = None
    conclusions: Optional[str] = None
    recommendations: Optional[str] = None
    confidence: Optional[float] = None
    has_tumor: Optional[bool] = None
    medical_context: Optional[str] = None

class Prediction(PredictionBase):
    id: int
    user_id: int
    created_at: datetime
    patient: Optional[PatientInfo] = None
    owner: Optional[DoctorInfo] = None

    model_config = ConfigDict(from_attributes=True)

class PredictionInDB(Prediction):
    pass

class PredictionList(BaseModel):
    items: List[Prediction]
    total: int
    page: int
    size: int
    pages: int
