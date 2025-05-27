from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.email import send_verification_email
from app.api import deps
from app.schemas.user import User, UserCreate
from app.crud.crud_user import crud_user

router = APIRouter()

@router.post("/login", response_model=dict)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create(db, obj_in=user_in)
    
    # Создаем токен для верификации
    verification_token = security.create_access_token(
        user.id,
        expires_delta=timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)
    )
    
    # Отправляем email с ссылкой для подтверждения
    send_verification_email(email_to=user.email, token=verification_token)
    
    return user

@router.post("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Verify email with token
    """
    try:
        payload = security.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid token"
            )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )
    
    user = crud_user.get(db, id=int(user_id))
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )
    
    user = crud_user.update(db, db_obj=user, obj_in={"is_active": True})
    return {"message": "Email verified successfully"} 