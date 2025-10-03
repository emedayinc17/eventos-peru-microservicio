FROM python:3.12-slim AS base
WORKDIR /app

COPY services/proveedores-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/libs
COPY services/proveedores-service /app/services/proveedores-service

ENV PYTHONPATH=/app/libs/shared:/app/services/proveedores-service
WORKDIR /app/services/proveedores-service

ENV PORT=8000
CMD ["sh","-lc","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
