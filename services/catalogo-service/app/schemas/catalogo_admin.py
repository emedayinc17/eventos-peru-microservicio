from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import date

# ===== IN =====
class TipoEventoIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class ServicioIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo_evento_id: str

class OpcionServicioIn(BaseModel):
    servicio_id: str
    nombre: str
    detalles: Optional[Any] = None  # dict -> JSON en repo

class PrecioOpcionIn(BaseModel):
    opcion_servicio_id: str
    moneda: str = "PEN"
    monto: float = Field(..., ge=0)
    vigente_desde: date
    vigente_hasta: Optional[date] = None

class PaqueteIn(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

class PaqueteUpdateIn(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)

class ItemPaqueteIn(BaseModel):
    paquete_id: str
    opcion_servicio_id: str
    cantidad: int = Field(1, ge=1)

class PrecioPaqueteIn(BaseModel):
    paquete_id: str
    moneda: str = "PEN"
    monto: float = Field(..., ge=0)
    vigente_desde: date
    vigente_hasta: Optional[date] = None

# ===== OUT =====
class TipoEventoOut(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    status: int

class ServicioOut(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    tipo_evento_id: str
    status: int

class OpcionServicioOut(BaseModel):
    id: str
    servicio_id: str
    nombre: str
    detalles: Optional[Any] = None
    status: int

class PrecioOpcionOut(BaseModel):
    id: str
    opcion_servicio_id: str
    moneda: str
    monto: float
    vigente_desde: str
    vigente_hasta: Optional[str] = None

class PaqueteOut(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    status: int

class ItemPaqueteOut(BaseModel):
    id: str
    paquete_id: str
    opcion_servicio_id: str
    cantidad: int

class PrecioPaqueteOut(BaseModel):
    id: str
    paquete_id: str
    moneda: str
    monto: float
    vigente_desde: str
    vigente_hasta: Optional[str] = None

class PaqueteListOut(BaseModel):
    items: List[PaqueteOut]
    page: int
    size: int
    total: int
