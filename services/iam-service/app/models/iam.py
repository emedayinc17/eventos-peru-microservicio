from sqlalchemy import Column, String, Integer, DateTime, JSON, SmallInteger, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "ev_iam"}

    id = Column(String(36), primary_key=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(150))
    telefono = Column(String(50))
    status = Column(TINYINT, nullable=False, default=1)
    last_login = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_deleted = Column(TINYINT, nullable=False, default=0)

class Rol(Base):
    __tablename__ = "rol"
    __table_args__ = {"schema": "ev_iam"}

    id = Column(String(36), primary_key=True)
    codigo = Column(String(50), nullable=False, unique=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(String(255))
    status = Column(TINYINT, nullable=False, default=1)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class UsuarioRol(Base):
    __tablename__ = "usuario_rol"
    __table_args__ = (UniqueConstraint("usuario_id", "rol_id", name="uq_usuario_rol"),
                      {"schema": "ev_iam"})

    id = Column(String(36), primary_key=True)
    usuario_id = Column(String(36), nullable=False)
    rol_id = Column(String(36), nullable=False)

class EventoAudit(Base):
    __tablename__ = "evento_audit"
    __table_args__ = {"schema": "ev_iam"}

    id = Column(String(36), primary_key=True)
    fecha_hora = Column(DateTime)
    actor_id = Column(String(36))
    entidad = Column(String(80), nullable=False)
    entidad_id = Column(String(36), nullable=False)
    accion = Column(String(40), nullable=False)
    metadata = Column(JSON)
