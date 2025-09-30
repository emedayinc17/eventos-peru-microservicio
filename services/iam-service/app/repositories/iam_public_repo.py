from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from app.core.security import hash_password

def _uuid(): return str(uuid.uuid4())

def email_existe(db: Session, email: str) -> bool:
    return bool(db.execute(text(
        "SELECT 1 FROM ev_iam.usuario WHERE email=:e AND is_deleted=0"
    ), {"e": email}).scalar())

def get_rol_cliente_id(db: Session) -> str | None:
    return db.execute(text(
        "SELECT id FROM ev_iam.rol WHERE codigo='CLIENTE' AND status=1 LIMIT 1"
    )).scalar()

def crear_usuario_cliente(db: Session, email: str, password: str,
                          nombre: str | None, telefono: str | None) -> dict:
    if email_existe(db, email):
        return {"error": "email_exists"}

    rid = get_rol_cliente_id(db)
    if not rid:
        return {"error": "rol_cliente_missing"}

    user_id = _uuid()
    db.execute(text("""
        INSERT INTO ev_iam.usuario (id,email,password_hash,nombre,telefono,status)
        VALUES (:id,:e,:p,:n,:t,1)
    """), {
        "id": user_id,
        "e": email,
        "p": hash_password(password),
        "n": nombre,
        "t": telefono,   # ← se inserta el teléfono
    })

    db.execute(text("""
        INSERT INTO ev_iam.usuario_rol (id,usuario_id,rol_id)
        VALUES (UUID(), :u, :r)
        ON DUPLICATE KEY UPDATE usuario_id=VALUES(usuario_id), rol_id=VALUES(rol_id)
    """), {"u": user_id, "r": rid})

    db.commit()

    # Devuelve lo guardado en BD (si quisieras mostrarlo en el público)
    row = db.execute(text("""
        SELECT id, email, nombre, telefono, status
        FROM ev_iam.usuario WHERE id=:id
    """), {"id": user_id}).mappings().first()
    return dict(row) if row else {"id": user_id, "email": email}
