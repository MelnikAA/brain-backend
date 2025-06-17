from typing import Any
from fastapi import APIRouter, Depends, Request
import logging

from app.api import deps
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=dict)
def whoami(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    logger.info(f"Whoami request headers: {request.headers}")
    logger.info(f"Whoami request from: {request.client.host}")
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    } 