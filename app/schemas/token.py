from typing import Optional
from pydantic import BaseModel

class TokenRequest(BaseModel):
    username: str
    password: str
    grant_type: str = "password"
    scope: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None 