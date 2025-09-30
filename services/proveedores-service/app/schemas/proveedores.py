from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DisponibilidadQuery(BaseModel):
    proveedor_id: str
    inicio: datetime
    fin: datetime

class IntervaloOcupado(BaseModel):
    # Para que el front pinte ocupados (turnos y holds confirmados/vigentes)
    inicio: datetime
    fin: datetime
    fuente: str  # "turno" | "hold"

class CrearHoldIn(BaseModel):
    proveedor_id: str
    opcion_servicio_id: str
    inicio: datetime
    fin: datetime
    minutos_validez: int = Field(default=20, ge=1, le=240)  # TTL del hold
    correlation_id: str | None = None  # si lo envías desde front/gateway

class HoldOut(BaseModel):
    id: str
    status: int
    expira_en: datetime

class ProveedorOut(BaseModel):
    id: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    rating_prom: Optional[float] = 0.0
    status: int

class ListarProveedoresQuery(BaseModel):
    servicio_id: str = Field(..., description="ID del servicio")
    q: Optional[str] = Field(None, description="Filtro por nombre (like)")
    page: int = 1
    size: int = 20

class LiberarHoldPath(BaseModel):
    hold_id: str
