from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate

class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    def get_multi_with_search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Patient]:
        """
        Получение списка пациентов с возможностью поиска
        """
        query = db.query(self.model)
        
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    Patient.full_name.ilike(search),
                    Patient.external_id.ilike(search)
                )
            )
        
        return query.offset(skip).limit(limit).all()

crud_patient = CRUDPatient(Patient) 