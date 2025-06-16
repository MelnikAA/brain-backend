from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    external_id = Column(String, nullable=True)  # Внешний ID для связи с другими системами

    predictions = relationship("Prediction", back_populates="patient") 