# app/api/iam/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.iam import LoginIn, TokenOut, MeOut
from app.repositories.iam_repo import (
    get_user_by_email, get_user_roles, get_user_by_id
)
from app.core.security import verify_password, create_jwt

router = APIRouter(prefix="/iam", tags=["IAM"])

@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    roles = get_user_roles(db, user["id"])
    token = create_jwt(sub=user["id"], email=user["email"], roles=roles)
    return {"access_token": token, "token_type": "Bearer"}

# app/api/iam/router.py (solo el /users/me)
@router.get("/users/me", response_model=MeOut)
def me(db: Session = Depends(get_db), current=Depends(get_current_user)):
    row = get_user_by_id(db, current["sub"])
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    roles = current.get("roles") or get_user_roles(db, current["sub"])
    return {
        "id": row["id"],
        "email": row["email"],
        "nombre": row.get("nombre"),
        "telefono": row.get("telefono"),  # ← aparece en la respuesta
        "roles": roles
    }

