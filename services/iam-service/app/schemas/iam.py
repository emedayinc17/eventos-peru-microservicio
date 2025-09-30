from pydantic import BaseModel, EmailStr

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class MeOut(BaseModel):
    id: str
    email: EmailStr
    nombre: str | None = None
    telefono: str | None = None 
    roles: list[str] = []
