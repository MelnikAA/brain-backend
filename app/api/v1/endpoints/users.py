from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr, BaseModel
from sqlalchemy.orm import Session
import logging

from app import crud, schemas
from app.models.user import User
from app.api import deps
from app.core.config import settings
from app.core.email import send_email
from app.core.security import generate_password_set_token

logger = logging.getLogger(__name__)

class PasswordResetResponse(BaseModel):
    message: str
    user_id: int
    email: str

router = APIRouter()

@router.get("/", response_model=schemas.user.UserList)
def read_users(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    Only for superusers.
    """
    skip = (page - 1) * size
    users = crud.user.get_multi(db, skip=skip, limit=size)
    total = crud.user.count(db)
    pages = (total + size - 1) // size
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.post("/", response_model=schemas.user.User)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = crud.user.create(db, obj_in=user_in)
    
    # Если пароль не указан, генерируем токен для установки пароля
    if not user_in.password and settings.EMAILS_ENABLED:
        try:
            token = generate_password_set_token(user.email)
            # Формируем URL для фронтенда
            frontend_url = settings.FRONTEND_URL.rstrip('/')
            password_set_url = f"{frontend_url}/set-password?token={token}&email={user.email}"
            
            await send_email(
                email_to=user.email,
                subject_template="Установите пароль",
                html_template_name="set_password.html",
                environment={
                    "project_name": settings.PROJECT_NAME,
                    "username": user.email,
                    "token": token,
                    "password_set_url": password_set_url
                },
            )
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
    
    return user

@router.put("/me", response_model=schemas.user.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.user.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.user.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/{user_id}", response_model=schemas.user.User)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

@router.put("/{user_id}", response_model=schemas.user.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.user.UserUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=schemas.user.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Удалить пользователя.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден",
        )
    user = crud.user.remove(db, id=user_id)
    return user

@router.post("/{user_id}/reset-password-request", response_model=PasswordResetResponse)
async def request_password_reset(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Request password reset for a user.
    Sends an email with a link to set a new password.
    Only for superusers.
    """
    try:
        user = crud.user.get(db, id=user_id)
        if not user:
            logger.error(f"User with id {user_id} not found")
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        
        # Создаем токен для установки пароля
        token = crud.user.create_password_set_token(db, user=user)
        
        # Отправляем email с токеном
        if not settings.EMAILS_ENABLED:
            logger.error("Email sending is disabled in settings")
            raise HTTPException(
                status_code=400,
                detail="Email sending is disabled"
            )

        # Формируем URL для фронтенда
        frontend_url = settings.FRONTEND_URL.rstrip('/')  # Убираем trailing slash если есть
        password_set_url = f"{frontend_url}/set-password?token={token}&email={user.email}"
        
        logger.info(f"Generated password reset URL: {password_set_url}")
        
        await send_email(
            email_to=user.email,
            subject_template="Сброс пароля",
            html_template_name="password_set.html",
            environment={
                "project_name": settings.PROJECT_NAME,
                "password_set_url": password_set_url,
                "email": user.email
            },
        )
        
        return {
            "message": "Password reset email has been sent successfully",
            "user_id": user.id,
            "email": user.email
        }
        
    except Exception as e:
        logger.error(f"Error in request_password_reset: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send password reset email: {str(e)}"
        ) 