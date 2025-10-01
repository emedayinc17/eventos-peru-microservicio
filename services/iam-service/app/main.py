import os
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

# Routers del dominio IAM (según tu repo)
from app.api.iam.router import router as iam_router
from app.api.iam.public_router import router as iam_public_router
from app.api.iam.admin_router import router as iam_admin_router

BASE_PATH = os.getenv("BASE_PATH", "")  # p.ej. "/iam"

app = FastAPI(
    title="iam-service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    root_path=BASE_PATH or ""
)

# Público / autenticación y endpoints de dominio
app.include_router(iam_public_router, prefix="/v1")
app.include_router(iam_router,        prefix="/v1")
# Administración IAM
app.include_router(iam_admin_router,  prefix="/v1/admin")

@app.get("/health")
def health():
    return {"service": "iam-service", "ok": True}

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_swagger_ui_html(openapi_url=external_spec, title=f"{app.title} - Swagger UI")

@app.get("/redoc", include_in_schema=False)
def custom_redoc(request: Request):
    external_spec = f"{BASE_PATH}{app.openapi_url}"
    return get_redoc_html(openapi_url=external_spec, title=f"{app.title} - ReDoc")
