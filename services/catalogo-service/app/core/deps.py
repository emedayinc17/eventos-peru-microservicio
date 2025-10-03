# app/core/deps.py
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.session import SessionLocal
from ev_shared.security import decode_jwt
from typing import Iterable
from app.repositories.iam_repo import get_user_roles  # ← usa tu función
from jwt import ExpiredSignatureError, InvalidTokenError

security = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)  # ← para fallback de roles
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")

    raw = credentials.credentials.strip()
    token = raw[7:].strip() if raw.lower().startswith("bearer ") else raw

    try:
        user = decode_jwt(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Fallback para tokens antiguos: si no hay roles en el token, los leemos de BD
    if not user.get("roles"):
        try:
            user["roles"] = [r.upper() for r in get_user_roles(db, user["sub"])]
        except Exception:
            user["roles"] = []

    return user

def get_correlation_id(x_correlation_id: str | None = Header(default=None)) -> str | None:
    return x_correlation_id

def require_roles(required: Iterable[str]):
    req = {str(r).upper() for r in required}
    def _dep(user = Depends(get_current_user)):
        roles = {str(r).upper() for r in (user.get("roles") or [])}
        if roles.isdisjoint(req):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "forbidden", "msg": "Rol insuficiente", "required": list(req)}
            )
        return user
    return _dep
