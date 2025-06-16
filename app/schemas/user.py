from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: Optional[str] = None

class SetPassword(BaseModel):
    password: constr(min_length=8, max_length=100)

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserList(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int
    pages: int 