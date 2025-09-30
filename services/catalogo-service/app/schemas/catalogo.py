from pydantic import BaseModel
from typing import Any

class TipoEventoOut(BaseModel):
    id: str
    nombre: str
    descripcion: str | None = None
    status: int

class ServicioOut(BaseModel):
    id: str
    nombre: str
    descripcion: str | None = None
    tipo_evento_id: str
    status: int

class OpcionPrecioOut(BaseModel):
    opcion_id: str
    servicio_id: str
    nombre: str
    detalles: Any | None
    moneda: str
    monto: float

class PaqueteDetalleOut(BaseModel):
    paquete_id: str
    codigo: str
    nombre: str
    descripcion: str | None = None
    status: int
    opcion_servicio_id: str
    cantidad: int
    moneda: str
    monto: float
