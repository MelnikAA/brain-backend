from sqlalchemy import Column, Integer, LargeBinary, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # Оригинальное имя файла
    content_type = Column(String, nullable=False)  # MIME-тип изображения
    data = Column(LargeBinary, nullable=False)  # Бинарные данные изображения
    created_at = Column(DateTime, default=datetime.utcnow)
    
    predictions = relationship("Prediction", back_populates="image") 