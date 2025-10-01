import os
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

# Routers del dominio Catálogo (según tu repo)
from app.api.catalogo.router import router as catalogo_router
from app.api.catalogo.admin_router import router as catalogo_admin_router

BASE_PATH = os.getenv("BASE_PATH", "")  # p.ej. "/catalogo" en k8s; "" en local

app = FastAPI(
    title="catalogo-service",
    version="1.0.0",
    docs_url=None,            # desactivar docs default
    redoc_url=None,           # desactivar redoc default
    openapi_url="/openapi.json",
    root_path=BASE_PATH or "" # útil para generar URLs absolutas correctas
)

# Público / dominio Catálogo
app.include_router(catalogo_router,       prefix="/v1")
# Administración Catálogo
app.include_router(catalogo_admin_router, prefix="/v1/admin")

@app.get("/health")
def health():
    return {"service": "catalogo-service", "ok": True}

# ---- Docs personalizados (apuntan al spec detrás del prefijo) ----
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_swagger_ui_html(openapi_url=external_spec, title=f"{app.title} - Swagger UI")

@app.get("/redoc", include_in_schema=False)
def custom_redoc(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_redoc_html(openapi_url=external_spec, title=f"{app.title} - ReDoc")
