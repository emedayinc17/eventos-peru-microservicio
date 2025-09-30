from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Compatibilidad Pydantic v2 y v1 para extra="forbid"
try:
    from pydantic import ConfigDict
    _MODEL_CONFIG_V2 = ConfigDict(extra="forbid")
    _IS_V2 = True
except Exception:
    _IS_V2 = False

class UserCreateIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nombre: Optional[str] = None
    telefono: Optional[str] = None  # 👈 importante
    status: int = 1

    if _IS_V2:
        model_config = _MODEL_CONFIG_V2
    else:
        class Config:
            extra = "forbid"

class AssignRolesIn(BaseModel):
    user_id: str
    roles: List[str]

class AdminUserOut(BaseModel):
    id: str
    email: EmailStr
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    status: int

class AssignRolesOut(BaseModel):
    user_id: str
    assigned: List[str]
    missing: List[str]
