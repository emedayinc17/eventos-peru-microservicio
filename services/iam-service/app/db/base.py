from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Importa modelos para que Alembic/metadata (si lo usas) los conozca
from app.models import iam, catalogo, paquetes, proveedores, contratacion  # noqa
