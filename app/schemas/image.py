from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ImageBase(BaseModel):
    filename: str
    content_type: str

class ImageCreate(ImageBase):
    data: bytes

class Image(ImageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 