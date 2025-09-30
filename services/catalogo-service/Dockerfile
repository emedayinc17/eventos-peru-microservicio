FROM python:3.12-slim

WORKDIR /app

# 1) Dependencias
COPY services/catalogo-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2) Librerías compartidas (si las usas)
COPY libs /app/libs

# 3) Código del servicio
COPY services/catalogo-service /app/services/catalogo-service

# 4) Rutas de import y directorio de trabajo
ENV PYTHONPATH=/app/libs:/app/services/catalogo-service
WORKDIR /app/services/catalogo-service

# 5) Arranque
CMD ["sh","-lc","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir /app/services/catalogo-service"]
