from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProveedorIn(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    status: int = 1

class ProveedorUpdateIn(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)

class ProveedorOut(BaseModel):
    id: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    rating_prom: Optional[float] = 0.0
    status: int

class HabilidadIn(BaseModel):
    proveedor_id: str
    servicio_id: str
    nivel: int = Field(1, ge=1, le=5)

class HabilidadesIn(BaseModel):
    servicio_ids: List[str]

class CalendarioSlotIn(BaseModel):
    proveedor_id: str
    inicio: datetime
    fin: datetime
    tipo: int = Field(..., description="1=turno, 2=descanso")
