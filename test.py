from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
h = pwd.hash("Admin_2025!")
print(h, len(h))


#docker run --rm -p 8000:8000 --env-file .env  eventos-peru-api:0.1.0
#Admin_2025
#Demo_2025
#Cliente@2025


#pytest --html=report.html --self-contained-html -vv

#uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


# IAM
#export $(cat services/iam-service/.env | xargs)  # (opcional) o confía en tu loader
#uvicorn services.iam-service.app.main:app --host 0.0.0.0 --port 8010 --reload
#
## Catálogo
#uvicorn services.catalogo-service.app.main:app --host 0.0.0.0 --port 8020 --reload
#
## Proveedores
#uvicorn services.proveedores-service.app.main:app --host 0.0.0.0 --port 8030 --reload
#
## Contratación
#uvicorn services.contratacion-service.app.main:app --host 0.0.0.0 --port 8040 --reload