from pydantic import BaseModel
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    version: str
    description: str | None = None

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 