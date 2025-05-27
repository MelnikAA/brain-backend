from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String)
    prediction_result = Column(Float)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions") 