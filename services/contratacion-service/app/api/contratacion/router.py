from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, get_correlation_id, require_roles
from app.schemas.contratacion import (
    CrearPedidoIn, PedidoOut, CrearItemIn, ItemOut, CrearReservaIn, ReservaOut, TransicionPedidoIn
)
from app.repositories.contratacion_repo import (
    crear_pedido, add_item, crear_reserva_con_chk,
    confirmar_pedido, cancelar_pedido, ejecutar_pedido
)

router = APIRouter(prefix="/contratacion", tags=["Contratación"], dependencies=[Depends(get_current_user)])

@router.post("/v1/pedidos", response_model=PedidoOut)
def post_pedido(
    payload: CrearPedidoIn,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    corr_id: str | None = Depends(get_correlation_id),
    x_request_id: str | None = Header(default=None)
):
    ped = crear_pedido(
        db=db,
        cliente_id=user["sub"],
        tipo_evento_id=payload.tipo_evento_id,
        fecha_evento=payload.fecha_evento,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
        ubicacion=payload.ubicacion,
        moneda="PEN",
        request_id=x_request_id,
        created_by=user["sub"],
        correlation_id=corr_id
    )
    return ped

@router.post("/v1/pedidos/{pedido_id}/items", response_model=ItemOut)
def post_item(
    pedido_id: str,
    payload: CrearItemIn,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return add_item(
        db=db, pedido_id=pedido_id, tipo_item=payload.tipo_item,
        referencia_id=payload.referencia_id, cantidad=payload.cantidad,
        precio_unit=payload.precio_unit, created_by=user["sub"]
    )

# Reservar (consumiendo hold y validando solape) — anidado bajo /pedidos/{id}
@router.post("/v1/pedidos/{pedido_id}/reservas", response_model=ReservaOut, status_code=201)
def post_reserva(
    pedido_id: str,
    body: CrearReservaIn,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["CLIENTE","ADMIN"]))
):
    row, err = crear_reserva_con_chk(
        db,
        item_pedido_id=body.item_pedido_id,
        proveedor_id=body.proveedor_id,
        inicio=body.inicio,
        fin=body.fin,
        hold_id=body.hold_id,
        actor_id=(user["sub"] if isinstance(user, dict) else getattr(user, "id", None))
    )
    if err == "conflict":
        raise HTTPException(status_code=409, detail={"error":"overlap","msg":"Proveedor ocupado en ese rango"})
    return row

@router.post("/v1/pedidos/{pedido_id}/confirmar", status_code=200)
def post_confirmar_pedido(
    pedido_id: str,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["CLIENTE","ADMIN"]))
):
    updated = confirmar_pedido(db, pedido_id, actor_id=(user["sub"] if isinstance(user, dict) else getattr(user, "id", None)))
    if updated == 0:
        raise HTTPException(status_code=409, detail={"error":"no_confirmable","msg":"Faltan reservas confirmadas"})
    return {"ok": True, "status": "CONFIRMADO", "pedido_id": pedido_id}

@router.post("/v1/pedidos/{pedido_id}/cancelar", status_code=200)
def post_cancelar_pedido(
    pedido_id: str,
    body: TransicionPedidoIn,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["CLIENTE","ADMIN"]))
):
    updated = cancelar_pedido(db, pedido_id, actor_id=(user["sub"] if isinstance(user, dict) else getattr(user, "id", None)), motivo=body.motivo)
    if updated == 0:
        raise HTTPException(status_code=409, detail={"error":"no_cancelable","msg":"Estado no permite cancelación"})
    return {"ok": True, "status": "CANCELADO", "pedido_id": pedido_id}

@router.post("/v1/pedidos/{pedido_id}/ejecutar", status_code=200)
def post_ejecutar_pedido(
    pedido_id: str,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["ADMIN"]))
):
    updated = ejecutar_pedido(db, pedido_id, actor_id=(user["sub"] if isinstance(user, dict) else getattr(user, "id", None)))
    if updated == 0:
        raise HTTPException(status_code=409, detail={"error":"no_ejecutable","msg":"Debe estar CONFIRMADO"})
    return {"ok": True, "status": "EJECUTADO", "pedido_id": pedido_id}
