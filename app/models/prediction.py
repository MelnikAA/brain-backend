from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Boolean, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    description = Column(Text, nullable=False)
    conclusions = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    has_tumor = Column(Boolean, nullable=False)
    medical_context = Column(Text, nullable=False)
    segmentation_mask = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="predictions")
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    patient = relationship("Patient", back_populates="predictions")
    
    image = relationship("Image", back_populates="predictions") 