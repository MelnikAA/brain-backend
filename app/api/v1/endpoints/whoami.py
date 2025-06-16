from typing import Any
from fastapi import APIRouter, Depends

from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=dict)
def whoami(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    } 