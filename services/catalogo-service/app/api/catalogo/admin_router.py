# app/api/catalogo/admin_router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_roles
from app.schemas.catalogo_admin import (
    # IN
    TipoEventoIn, ServicioIn, OpcionServicioIn, PrecioOpcionIn,
    PaqueteIn, PaqueteUpdateIn, ItemPaqueteIn, PrecioPaqueteIn,
    # OUT
    TipoEventoOut, ServicioOut, OpcionServicioOut, PrecioOpcionOut,
    PaqueteOut, ItemPaqueteOut, PrecioPaqueteOut, PaqueteListOut
)
from app.repositories.catalogo_admin_repo import (
    crear_tipo_evento, crear_servicio, crear_opcion, crear_precio_opcion,
    listar_paquetes_admin, crear_paquete, actualizar_paquete,
    add_item_paquete, eliminar_item_paquete, crear_precio_paquete
)

router = APIRouter(
    prefix="/api/catalogo/admin/v1",
    tags=["Catálogo - Admin"],
    dependencies=[Depends(get_current_user)]
)

# ===== tipos/servicios/opciones =====
@router.post("/tipos-evento", response_model=TipoEventoOut, status_code=201)
def post_tipo_evento(body: TipoEventoIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return crear_tipo_evento(db, body.nombre, body.descripcion, actor=user["sub"])

@router.post("/servicios", response_model=ServicioOut, status_code=201)
def post_servicio(body: ServicioIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return crear_servicio(db, body.nombre, body.descripcion, body.tipo_evento_id, actor=user["sub"])

@router.post("/opciones", response_model=OpcionServicioOut, status_code=201)
def post_opcion(body: OpcionServicioIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return crear_opcion(db, body.servicio_id, body.nombre, body.detalles, actor=user["sub"])

@router.post("/opciones/precios", response_model=PrecioOpcionOut, status_code=201)
def post_precio_opcion(body: PrecioOpcionIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return crear_precio_opcion(
        db, opcion_id=body.opcion_servicio_id, moneda=body.moneda, monto=body.monto,
        desde=body.vigente_desde, hasta=body.vigente_hasta, actor=user["sub"]
    )

# ===== paquetes =====
@router.get("/paquetes", response_model=PaqueteListOut)
def list_paquetes(q: str|None = Query(None), page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                  db: Session = Depends(get_db), _user=Depends(require_roles(["ADMIN"]))):
    items, total = listar_paquetes_admin(db, q, page, size)
    return {"items": items, "page": page, "size": size, "total": total}

@router.post("/paquetes", response_model=PaqueteOut, status_code=201)
def post_paquete(body: PaqueteIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    row, err = crear_paquete(db, body.codigo, body.nombre, body.descripcion, actor=user["sub"])
    if err == "dup":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de paquete ya existe")
    return row

@router.put("/paquetes/{paquete_id}", status_code=200)
def put_paquete(paquete_id: str, body: PaqueteUpdateIn, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    updated = actualizar_paquete(db, paquete_id, body.nombre, body.descripcion, body.status)
    if updated == 0:
        raise HTTPException(status_code=404, detail="Paquete no encontrado o sin cambios")
    return {"ok": True, "id": paquete_id}

# ===== items de paquete =====
@router.post("/paquetes/{paquete_id}/items", response_model=ItemPaqueteOut, status_code=201)
def post_item_paquete_rest(paquete_id: str, body: ItemPaqueteIn, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    # compat: si body trae paquete_id, lo ignoramos y usamos el path param
    return add_item_paquete(db, paquete_id, body.opcion_servicio_id, body.cantidad)

# Ruta legacy compatible con tu versión previa
@router.post("/paquetes/items", response_model=ItemPaqueteOut, status_code=201)
def post_item_paquete_legacy(body: ItemPaqueteIn, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    return add_item_paquete(db, body.paquete_id, body.opcion_servicio_id, body.cantidad)

@router.delete("/paquetes/{paquete_id}/items/{item_id}", status_code=204)
def delete_item_paquete(paquete_id: str, item_id: str, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    _ = eliminar_item_paquete(db, paquete_id, item_id)  # idempotente
    return

# ===== precios de paquete =====
@router.post("/paquetes/precios", response_model=PrecioPaqueteOut, status_code=201)
def post_precio_paquete(body: PrecioPaqueteIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return crear_precio_paquete(
        db, paquete_id=body.paquete_id, moneda=body.moneda, monto=body.monto,
        desde=body.vigente_desde, hasta=body.vigente_hasta, actor=user["sub"]
    )
