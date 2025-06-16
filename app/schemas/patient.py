from typing import Optional
from pydantic import BaseModel
from datetime import date

class PatientBase(BaseModel):
    full_name: str
    birth_date: date
    external_id: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int

    class Config:
        from_attributes = True 