# app/api/catalogo/router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db,get_current_user
from app.schemas.catalogo import TipoEventoOut, ServicioOut, OpcionPrecioOut, PaqueteDetalleOut
from app.repositories.catalogo_repo import (
    get_tipos_evento, get_servicios, get_opciones_con_precio_vigente, get_paquetes_detalle
)

router = APIRouter(prefix="/catalogo", tags=["Catálogo"], dependencies=[Depends(get_current_user)] )

@router.get("/v1/tipos-evento", response_model=list[TipoEventoOut])
def list_tipos_evento(db: Session = Depends(get_db)):
    return get_tipos_evento(db)

@router.get("/v1/servicios", response_model=list[ServicioOut])
def list_servicios(
    tipo_evento_id: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return get_servicios(db, tipo_evento_id)

@router.get("/v1/opciones", response_model=list[OpcionPrecioOut])
def list_opciones(servicio_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    return get_opciones_con_precio_vigente(db, servicio_id)

@router.get("/v1/paquetes", response_model=list[PaqueteDetalleOut])
def list_paquetes(db: Session = Depends(get_db)):
    return get_paquetes_detalle(db)
