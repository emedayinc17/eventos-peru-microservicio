# 1) Builder opcional si compilas wheels (mysqlclient, etc.)
FROM python:3.12-slim AS base
WORKDIR /app

# Dependencias del servicio (ajusta el nombre)
COPY services/iam-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Lib compartida y código del servicio
COPY libs /app/libs
COPY services/iam-service /app/services/iam-service

# Rutas de import: shared + servicio
ENV PYTHONPATH=/app/libs/shared:/app/services/iam-service
WORKDIR /app/services/iam-service

# Puerto por defecto
ENV PORT=8000

# Arranque
CMD ["sh","-lc","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
