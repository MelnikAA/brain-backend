from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password) if obj_in.password else None,
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_active=bool(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            update_data["is_active"] = True
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def count(self, db: Session) -> int:
        """
        Count total number of users in the database
        """
        return db.query(User).count()

    def create_password_set_token(self, db: Session, *, user: User) -> str:
        """
        Создает токен для установки пароля и сохраняет его в базе данных.
        Деактивирует пользователя до установки нового пароля.
        """
        from app.core.security import generate_password_set_token
        from datetime import datetime, timedelta

        token = generate_password_set_token(user.email)
        user.password_set_token = token
        user.password_set_token_expires = datetime.utcnow() + timedelta(hours=24)
        user.is_active = False
        db.add(user)
        db.commit()
        return token


user = CRUDUser(User) 