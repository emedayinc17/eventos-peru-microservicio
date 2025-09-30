# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, List
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_jwt(*, sub: str, email: str, roles: List[str], expires_minutes: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp_minutes = expires_minutes or settings.JWT_EXPIRE_MIN
    payload = {
        "sub": sub,
        "email": email,
        "roles": [str(r).upper() for r in roles],  # ← opcional, normaliza
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
        "iss": settings.APP_NAME,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_jwt(token: str) -> Dict[str, Any]:
    # Leeway de 30s para evitar 401 por pequeños desfases de reloj
    claims = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALG],
        options={"require": ["sub", "exp", "iat"]},
        leeway=30,
    )
    # salida homogénea (no rompe: sólo reordena)
    roles = claims.get("roles") or []
    claims["roles"] = [str(r).upper() for r in roles]
    return claims
