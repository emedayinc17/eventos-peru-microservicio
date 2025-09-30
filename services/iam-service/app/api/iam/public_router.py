from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.iam_public import RegisterIn
from app.schemas.iam import TokenOut  # ya lo tienes
from app.repositories.iam_public_repo import crear_usuario_cliente
from app.core.security import create_jwt

router = APIRouter(prefix="/iam/public/v1", tags=["IAM - Public"])

@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    res = crear_usuario_cliente(
        db, email=body.email, password=body.password,
        nombre=body.nombre, telefono=body.telefono
    )
    if "error" in res:
        if res["error"] == "email_exists":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email ya existe")
        if res["error"] == "rol_cliente_missing":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="rol CLIENTE no configurado")
        raise HTTPException(status_code=400, detail="registro inválido")

    # Auto-login: emite token con rol CLIENTE
    token = create_jwt(sub=res["id"], email=res["email"], roles=["CLIENTE"])
    return {"access_token": token, "token_type": "Bearer"}
