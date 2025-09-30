from fastapi import FastAPI

# Routers del dominio Catálogo (según tu repo)
from app.api.catalogo.router import router as catalogo_router
from app.api.catalogo.admin_router import router as catalogo_admin_router

app = FastAPI(title="catalogo-service", version="1.0.0")

# Público / dominio Catálogo
app.include_router(catalogo_router,       prefix="/v1")

# Administración Catálogo (tipos evento, servicios, opciones, paquetes, etc.)
app.include_router(catalogo_admin_router, prefix="/v1/admin")

@app.get("/health")
def health():
    return {"service": "catalogo-service", "ok": True}
