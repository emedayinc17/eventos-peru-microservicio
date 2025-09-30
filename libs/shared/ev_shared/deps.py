from typing import Iterable
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError

from .db import get_db  # reexport para usarlo desde aquí si quieres
from .security import decode_jwt

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 1) Validación del esquema
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")

    # 2) Saneamos por si llega "Bearer ey..." dentro del propio token
    raw = credentials.credentials.strip()
    token = raw[7:].strip() if raw.lower().startswith("bearer ") else raw

    # 3) Decodificar y devolver el payload, con errores claros
    try:
        return decode_jwt(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_correlation_id(x_correlation_id: str | None = Header(default=None)) -> str | None:
    return x_correlation_id

def require_roles(required: Iterable[str]):
    """
    Dependency de autorización por rol.
    Exige que el usuario tenga al menos uno de los roles indicados.
    Asume que get_current_user() devuelve un dict con "roles".
    """
    req = {str(r).upper() for r in required}

    def _dep(user = Depends(get_current_user)):
        roles = set()
        if isinstance(user, dict):
            raw = user.get("roles") or user.get("authorities") or []
        else:
            raw = getattr(user, "roles", []) or []
        roles = {str(r).upper() for r in raw}

        if roles.isdisjoint(req):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "forbidden", "msg": "Rol insuficiente", "required": list(req)}
            )
        return user
    return _dep
