import os
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

# Router del dominio Contratación (según tu repo)
from app.api.contratacion.router import router as contratacion_router

BASE_PATH = os.getenv("BASE_PATH", "")  # p.ej. "/contratacion"

app = FastAPI(
    title="contratacion-service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    root_path=BASE_PATH or ""
)

# Público / dominio Contratación
app.include_router(contratacion_router, prefix="/v1")

@app.get("/health")
def health():
    return {"service": "contratacion-service", "ok": True}

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_swagger_ui_html(openapi_url=external_spec, title=f"{app.title} - Swagger UI")

@app.get("/redoc", include_in_schema=False)
def custom_redoc(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_redoc_html(openapi_url=external_spec, title=f"{app.title} - ReDoc")
