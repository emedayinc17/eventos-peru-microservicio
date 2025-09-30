# schemas/contratacion.py (versión consolidada, sin duplicados)
from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional

class CrearPedidoIn(BaseModel):
    tipo_evento_id: str
    fecha_evento: date
    hora_inicio: time
    hora_fin: time | None = None
    ubicacion: str

class PedidoOut(BaseModel):
    id: str
    cliente_id: str
    tipo_evento_id: str
    fecha_evento: date
    hora_inicio: time
    hora_fin: time | None = None
    ubicacion: str
    monto_total: float
    moneda: str
    status: int

class CrearItemIn(BaseModel):
    tipo_item: int = Field(..., ge=1, le=2)  # 1=OPCION_SERVICIO, 2=PAQUETE
    referencia_id: str
    cantidad: int = Field(default=1, ge=1)
    precio_unit: float = Field(..., ge=0)

class ItemOut(BaseModel):
    id: str
    pedido_id: str
    tipo_item: int
    referencia_id: str
    cantidad: int
    precio_unit: float
    precio_total: float

class CrearReservaIn(BaseModel):
    item_pedido_id: str
    proveedor_id: str
    inicio: datetime
    fin: datetime
    hold_id: str | None = None

class ReservaOut(BaseModel):
    id: str
    item_pedido_id: str
    proveedor_id: str
    inicio: datetime
    fin: datetime
    status: int
    hold_id: str | None = None

class TransicionPedidoIn(BaseModel):
    motivo: Optional[str] = Field(None, description="Motivo (para cancelación)")
