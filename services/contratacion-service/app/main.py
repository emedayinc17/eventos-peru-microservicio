from fastapi import FastAPI

# Router del dominio Contratación (según tu repo)
from app.api.contratacion.router import router as contratacion_router

app = FastAPI(title="contratacion-service", version="1.0.0")

# Público / dominio Contratación (pedido, ítems, reservas, confirmar, cancelar…)
app.include_router(contratacion_router, prefix="/v1")

@app.get("/health")
def health():
    return {"service": "contratacion-service", "ok": True}
