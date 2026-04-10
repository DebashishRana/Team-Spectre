from pydantic import BaseModel, EmailStr

class AuthRequest(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    country: str | None = None
    receive_updates: bool = False
