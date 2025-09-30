# app/repositories/iam_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_user_by_email(db: Session, email: str):
    q = text("""SELECT id, email, password_hash, nombre, telefono
                FROM ev_iam.usuario
                WHERE email=:em AND is_deleted=0 AND status=1""")
    row = db.execute(q, {"em": email}).mappings().first()
    return dict(row) if row else None

def get_user_by_id(db: Session, user_id: str):
    q = text("""SELECT id, email, nombre, telefono
                FROM ev_iam.usuario
                WHERE id=:uid AND is_deleted=0 AND status=1""")
    row = db.execute(q, {"uid": user_id}).mappings().first()
    return dict(row) if row else None

def get_user_roles(db: Session, user_id: str) -> list[str]:
    q = text("""SELECT r.codigo
                FROM ev_iam.usuario_rol ur
                JOIN ev_iam.rol r ON r.id = ur.rol_id
                WHERE ur.usuario_id=:uid AND r.status=1""")
    return [r[0] for r in db.execute(q, {"uid": user_id}).all()]
