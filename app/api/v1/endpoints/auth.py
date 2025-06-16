from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.email import send_verification_email
from app.api import deps
from app.schemas.user import User, UserCreate
from app.schemas.token import TokenRequest, Token
from app.utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)

router = APIRouter()

@router.post("/set-password", response_model=dict)
def set_password(
    *,
    db: Session = Depends(deps.get_db),
    token: str = Body(...),
    password: str = Body(...),
    email: str = Body(...),
) -> Any:
    """
    Установка пароля по токену.
    """
    try:
        payload = security.decode_token(token)
        if payload.get("type") != "password_set":
            raise HTTPException(
                status_code=400,
                detail="Invalid token type"
            )
        token_email = payload.get("sub")
        if not token_email or token_email != email:
            raise HTTPException(
                status_code=400,
                detail="Invalid token or email"
            )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )
    
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Обновляем пароль пользователя и активируем его
    user.hashed_password = get_password_hash(password)
    user.is_active = True  # Активируем пользователя после установки пароля
    user.password_set_token = None  # Очищаем токен
    user.password_set_token_expires = None  # Очищаем время истечения токена
    db.add(user)
    db.commit()
    
    return {"message": "Password set successfully"}

@router.post("/login", response_model=Token)
async def login(
    *,
    db: Session = Depends(deps.get_db),
    username: str = Form(...),
    password: str = Form(...),
    grant_type: str = Form("password"),
    scope: str = Form(None),
) -> Any:
    """
    Аутентификация пользователя и получение JWT токена.

    Args:
        db: Сессия базы данных
        username: Email пользователя
        password: Пароль пользователя
        grant_type: Тип гранта (по умолчанию "password")
        scope: Область доступа (опционально)

    Returns:
        Token: Токен доступа
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
            "token_type": "bearer",
            "scope": "web"
        }

    Raises:
        HTTPException: 
            401 - Неверный email или пароль
            400 - Неподдерживаемый grant_type
    """
    if grant_type != "password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type"
        )

    user = crud.user.authenticate(
        db, email=username, password=password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
        scope=scope
    )

@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Регистрация нового пользователя.

    Args:
        db: Сессия базы данных
        user_in: Данные нового пользователя
            {
                "email": "user@example.com",
                "password": "strongpassword",
                "full_name": "John Doe",
                "is_superuser": false
            }

    Returns:
        User: Созданный пользователь

    Raises:
        HTTPException: 400 - Пользователь с таким email уже существует
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    
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
    Подтверждение email пользователя по токену.

    Args:
        token: Токен подтверждения
        db: Сессия базы данных

    Returns:
        dict: Сообщение об успешном подтверждении
        {
            "message": "Email verified successfully"
        }

    Raises:
        HTTPException: 
            400 - Неверный токен или email уже подтвержден
            404 - Пользователь не найден
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
    
    user = crud.user.get(db, id=int(user_id))
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
    
    user = crud.user.update(db, db_obj=user, obj_in={"is_active": True})
    return {"message": "Email verified successfully"}

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=User)
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/password-recovery/{email}", response_model=Any)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    # TODO: Send email with password reset token
    return {"msg": "Password recovery email sent"}

@router.post("/reset-password/", response_model=Any)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"} 