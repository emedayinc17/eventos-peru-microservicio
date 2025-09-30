FROM python:3.12-slim

WORKDIR /app

# Dependencias del servicio IAM
COPY services/iam-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Librerías compartidas (si las usas)
COPY libs /app/libs

# Código del servicio
COPY services/iam-service /app/services/iam-service

# Rutas de import
ENV PYTHONPATH=/app/libs:/app/services/iam-service
WORKDIR /app/services/iam-service

# Arranque (ajusta si tu main está en otra ruta)
CMD ["sh","-lc","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir /app/services/iam-service"]
