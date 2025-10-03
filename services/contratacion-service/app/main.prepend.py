# services/contratacion-service/app/main.py (patched header)
# Carga temprana de configuración para que .env/Vault estén disponibles antes de montar rutas
from ev_shared.config import settings  # noqa: F401

