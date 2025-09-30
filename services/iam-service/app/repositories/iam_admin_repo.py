# app/repositories/iam_admin_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from app.core.security import hash_password

def _uuid(): return str(uuid.uuid4())

def crear_usuario(db: Session, email: str, password: str,
                  nombre: str | None, telefono: str | None, status: int):
    user_id = _uuid()
    db.execute(text("""
        INSERT INTO ev_iam.usuario (id,email,password_hash,nombre,telefono,status)
        VALUES (:id,:e,:p,:n,:t,:s)
    """), {
        "id": user_id,
        "e": email,
        "p": hash_password(password),
        "n": nombre,
        "t": telefono,      # 👈 aquí va
        "s": status,
    })
    db.commit()
    row = db.execute(text("""
        SELECT id, email, nombre, telefono, status
        FROM ev_iam.usuario WHERE id=:id
    """), {"id": user_id}).mappings().first()
    return dict(row)

def _get_role_id_by_code(db: Session, code: str) -> str | None:
    return db.execute(text(
        "SELECT id FROM ev_iam.rol WHERE codigo=:c AND status=1 LIMIT 1"
    ), {"c": code}).scalar()

def assign_roles(db: Session, user_id: str, roles_codigos: list[str]):
    assigned, missing = [], []
    for code in [c.upper() for c in roles_codigos]:
        rid = _get_role_id_by_code(db, code)
        if not rid:
            missing.append(code); continue
        db.execute(text("""
            INSERT INTO ev_iam.usuario_rol (id,usuario_id,rol_id)
            VALUES (UUID(), :u, :r)
            ON DUPLICATE KEY UPDATE usuario_id=VALUES(usuario_id), rol_id=VALUES(rol_id)
        """), {"u": user_id, "r": rid})
        assigned.append(code)
    db.commit()
    return {"user_id": user_id, "assigned": assigned, "missing": missing}
