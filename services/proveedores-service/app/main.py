import os
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

# Routers del dominio Proveedores (según tu repo)
from app.api.proveedores.router import router as proveedores_router
from app.api.proveedores.admin_router import router as proveedores_admin_router

BASE_PATH = os.getenv("BASE_PATH", "")  # p.ej. "/proveedores"

app = FastAPI(
    title="proveedores-service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    root_path=BASE_PATH or ""
)

# Público / dominio Proveedores
app.include_router(proveedores_router,       prefix="/v1")
# Administración Proveedores
app.include_router(proveedores_admin_router, prefix="/v1/admin")

@app.get("/health")
def health():
    return {"service": "proveedores-service", "ok": True}

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_swagger_ui_html(openapi_url=external_spec, title=f"{app.title} - Swagger UI")

@app.get("/redoc", include_in_schema=False)
def custom_redoc(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_redoc_html(openapi_url=external_spec, title=f"{app.title} - ReDoc")
