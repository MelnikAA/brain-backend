from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_active_superuser, get_current_active_user
from app.schemas.user import User, UserCreate, UserUpdate
from app.crud import user as user_crud

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список пользователей
    """
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/create", response_model=User)
def create_user_by_superuser(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Создание нового пользователя суперпользователем
    """
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )
    user = user_crud.create(db, obj_in=user_in, created_by_superuser=True)
    return user

@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Создать нового пользователя
    """
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить пользователя по ID
    """
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить пользователя
    """
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}", response_model=User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить пользователя
    """
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.delete_user(db=db, user_id=user_id)

@router.put("/me/analysis-attempts", response_model=User)
def update_my_analysis_attempts(
    attempts: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить количество попыток анализа для текущего пользователя
    """
    if attempts < 0:
        raise HTTPException(
            status_code=400,
            detail="Количество попыток не может быть отрицательным"
        )
    return user_crud.update_analysis_attempts(db=db, user=current_user, attempts=attempts)

@router.get("/me/analysis-attempts", response_model=User)
def get_my_analysis_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о количестве попыток анализа для текущего пользователя
    """
    return current_user 