from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_roles
from app.schemas.proveedores_admin import (
    ProveedorIn, ProveedorUpdateIn, ProveedorOut,
    HabilidadIn, HabilidadesIn, CalendarioSlotIn
)
from app.repositories.proveedores_admin_repo import (
    crear_proveedor, actualizar_proveedor, desactivar_proveedor,
    add_habilidad, agregar_habilidades, quitar_habilidad, add_calendario_slot
)

router = APIRouter(
    prefix="/api/proveedores/admin/v1",
    tags=["Proveedores - Admin"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/proveedores", response_model=ProveedorOut, status_code=201)
def post_proveedor(body: ProveedorIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return crear_proveedor(db, body.nombre, body.email, body.telefono, body.status, actor=user["sub"])

@router.put("/proveedores/{proveedor_id}", status_code=200)
def put_proveedor(proveedor_id: str, body: ProveedorUpdateIn, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    updated = actualizar_proveedor(db, proveedor_id, body.nombre, body.email, body.telefono, body.status)
    if updated == 0:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado o sin cambios")
    return {"ok": True, "id": proveedor_id}

@router.delete("/proveedores/{proveedor_id}", status_code=204)
def delete_proveedor(proveedor_id: str, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    _ = desactivar_proveedor(db, proveedor_id)  # idempotente
    return

@router.post("/proveedores/{proveedor_id}/habilidades", status_code=200)
def post_habilidades(proveedor_id: str, body: HabilidadesIn, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    return agregar_habilidades(db, proveedor_id, body.servicio_ids)

@router.post("/habilidades", status_code=201)
def post_habilidad(body: HabilidadIn, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    return add_habilidad(db, body.proveedor_id, body.servicio_id, body.nivel)

@router.delete("/proveedores/{proveedor_id}/habilidades/{servicio_id}", status_code=204)
def delete_habilidad(proveedor_id: str, servicio_id: str, db: Session = Depends(get_db), _=Depends(require_roles(["ADMIN"]))):
    _ = quitar_habilidad(db, proveedor_id, servicio_id)
    return

@router.post("/calendario", status_code=201)
def post_calendario_slot(body: CalendarioSlotIn, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    return add_calendario_slot(db, body.proveedor_id, body.inicio, body.fin, body.tipo, actor=user["sub"])
