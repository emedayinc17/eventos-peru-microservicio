# app/api/proveedores/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_correlation_id, require_roles
from app.schemas.proveedores import (
    IntervaloOcupado,
    CrearHoldIn,
    HoldOut,
    ProveedorOut,
)
from app.repositories.proveedores_repo import (
    get_intervalos_ocupados,
    crear_hold,
    listar_proveedores,
    liberar_hold,
)

router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/v1", response_model=list[ProveedorOut])
def get_proveedores(
    servicio_id: str = Query(..., description="ID del servicio"),
    q: str | None = Query(None, description="Filtro por nombre (LIKE)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user = Depends(get_current_user),
):
    return listar_proveedores(db, servicio_id, q, page, size)


@router.get("/v1/{proveedor_id}/agenda", response_model=list[IntervaloOcupado])
def agenda(
    proveedor_id: str,
    desde: str = Query(..., description="Datetime ISO 8601"),
    hasta: str = Query(..., description="Datetime ISO 8601"),
    db: Session = Depends(get_db),
    _user = Depends(get_current_user),
):
    from datetime import datetime
    try:
        di = datetime.fromisoformat(desde)
        df = datetime.fromisoformat(hasta)
    except Exception:
        raise HTTPException(status_code=400, detail="Fechas inválidas (usar ISO 8601).")
    return get_intervalos_ocupados(db, proveedor_id, di, df)


# Compatibilidad con tu ruta previa (si el front la usa). Puedes quitarla cuando migres.
#@router.get("/v1/disponibilidad", response_model=list[IntervaloOcupado], deprecated=True)
#def disponibilidad(
#    proveedor_id: str = Query(...),
#    inicio: str = Query(..., description="Datetime ISO 8601"),
#    fin: str = Query(..., description="Datetime ISO 8601"),
#    db: Session = Depends(get_db),
#    _user = Depends(get_current_user),
#):
#    from datetime import datetime
#    try:
#        di = datetime.fromisoformat(inicio)
#        df = datetime.fromisoformat(fin)
#    except Exception:
#        raise HTTPException(status_code=400, detail="Fechas inválidas (usar ISO 8601).")
#    return get_intervalos_ocupados(db, proveedor_id, di, df)


# Holds bajo el proveedor (alineado al contrato). Nota:
# - CrearHoldIn tiene un campo proveedor_id, pero aquí usamos el del path.
#   Si llega en el body y no coincide, lo ignoramos (o podrías validar igualdad).
@router.post("/v1/{proveedor_id}/holds", response_model=HoldOut)
def post_hold(
    proveedor_id: str,
    payload: CrearHoldIn,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    corr_id: str | None = Depends(get_correlation_id),
):
    correlation_id = payload.correlation_id or corr_id
    row = crear_hold(
        db=db,
        proveedor_id=proveedor_id,
        opcion_servicio_id=payload.opcion_servicio_id,
        inicio=payload.inicio,
        fin=payload.fin,
        minutos_validez=payload.minutos_validez,
        created_by=user["sub"],
        correlation_id=correlation_id,
    )
    return {"id": row["id"], "status": row["status"], "expira_en": row["expira_en"]}


@router.delete("/v1/holds/{hold_id}", status_code=204)
def delete_hold(
    hold_id: str,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["CLIENTE", "ADMIN"])),
):
    _ = liberar_hold(
        db, hold_id, actor_id=(user["sub"] if isinstance(user, dict) else getattr(user, "id", None))
    )
    return
