from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# Compatibilidad Pydantic v2 y v1 para extra="forbid"
try:
    # Pydantic v2
    from pydantic import ConfigDict
    _MODEL_CONFIG_V2 = ConfigDict(extra="forbid")
    _IS_V2 = True
except Exception:
    _IS_V2 = False



class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nombre: Optional[str] = None
    telefono: Optional[str] = None  # 👈 importante

    if _IS_V2:
        model_config = _MODEL_CONFIG_V2
    else:
        class Config:
            extra = "forbid"
