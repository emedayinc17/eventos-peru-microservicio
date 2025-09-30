from fastapi import FastAPI

# Routers del dominio IAM (existen en tu repo)
from app.api.iam.router import router as iam_router
from app.api.iam.public_router import router as iam_public_router
from app.api.iam.admin_router import router as iam_admin_router

app = FastAPI(title="iam-service", version="1.0.0")

# Público / autenticación y endpoints de dominio
app.include_router(iam_public_router, prefix="/v1")
app.include_router(iam_router,        prefix="/v1")

# Administración IAM
app.include_router(iam_admin_router,  prefix="/v1/admin")

@app.get("/health")
def health():
    return {"service": "iam-service", "ok": True}
