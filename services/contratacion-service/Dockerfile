FROM python:3.12-slim AS base
WORKDIR /app

COPY services/contratacion-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/libs
COPY services/contratacion-service /app/services/contratacion-service

ENV PYTHONPATH=/app/libs/shared:/app/services/contratacion-service
WORKDIR /app/services/contratacion-service

ENV PORT=8000
CMD ["sh","-lc","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
