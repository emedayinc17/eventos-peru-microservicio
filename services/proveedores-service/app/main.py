from fastapi import FastAPI

# Routers del dominio Proveedores (según tu repo)
from app.api.proveedores.router import router as proveedores_router
from app.api.proveedores.admin_router import router as proveedores_admin_router

app = FastAPI(title="proveedores-service", version="1.0.0")

# Público / dominio Proveedores (listado, agenda, holds…)
app.include_router(proveedores_router,       prefix="/v1")

# Administración Proveedores (crear proveedor, habilidades, calendario…)
app.include_router(proveedores_admin_router, prefix="/v1/admin")

@app.get("/health")
def health():
    return {"service": "proveedores-service", "ok": True}
