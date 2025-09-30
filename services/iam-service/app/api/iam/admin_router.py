from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.deps import get_db, get_current_user, require_roles
from app.schemas.iam_admin import (
    UserCreateIn, AssignRolesIn,
    AdminUserOut, AssignRolesOut,
)
from app.repositories.iam_admin_repo import crear_usuario, assign_roles

log = logging.getLogger("uvicorn")

router = APIRouter(
    prefix="/iam/admin/v1",
    tags=["IAM - Admin"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/users", response_model=AdminUserOut, status_code=201)
def post_user(
    body: UserCreateIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["ADMIN"]))
):
    # LOG: para verificar qué llegó
    log.info(f"[ADMIN users] body.telefono={body.telefono!r}")

    exists = db.execute(text(
        "SELECT 1 FROM ev_iam.usuario WHERE email=:e AND is_deleted=0"
    ), {"e": body.email}).scalar()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email ya existe")

    return crear_usuario(db, body.email, body.password, body.nombre, body.telefono, body.status)

@router.post("/users/roles", response_model=AssignRolesOut)
def post_user_roles(
    body: AssignRolesIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["ADMIN"]))
):
    if not body.roles:
        raise HTTPException(status_code=400, detail="roles vacío")

    ok = db.execute(text(
        "SELECT 1 FROM ev_iam.usuario WHERE id=:u AND is_deleted=0"
    ), {"u": body.user_id}).scalar()
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="usuario no existe")

    res = assign_roles(db, body.user_id, body.roles)
    if not res["assigned"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "roles no válidos", "missing": res["missing"]}
        )
    return res
