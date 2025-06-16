from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.patient import Patient, PatientCreate, PatientUpdate
from app.crud.crud_patient import crud_patient
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Patient])
def read_patients(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=100, description="Максимальное количество записей"),
    search: Optional[str] = Query(None, description="Поиск по имени или внешнему ID"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получение списка пациентов с возможностью поиска и пагинации.
    """
    patients = crud_patient.get_multi_with_search(
        db=db,
        skip=skip,
        limit=limit,
        search=search
    )
    return patients

@router.post("/", response_model=Patient)
def create_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_in: PatientCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Создание нового пациента.
    """
    patient = crud_patient.create(db=db, obj_in=patient_in)
    return patient

@router.get("/{patient_id}", response_model=Patient)
def read_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получение информации о конкретном пациенте по ID.
    """
    patient = crud_patient.get(db=db, id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    patient_in: PatientUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Обновление информации о пациенте.
    """
    patient = crud_patient.get(db=db, id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    patient = crud_patient.update(db=db, db_obj=patient, obj_in=patient_in)
    return patient

@router.delete("/{patient_id}", response_model=Patient)
def delete_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Удаление пациента.
    """
    patient = crud_patient.get(db=db, id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    patient = crud_patient.remove(db=db, id=patient_id)
    return patient 