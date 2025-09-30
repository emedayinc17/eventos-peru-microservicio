
# en E:\eventos_peru  (raíz)
docker build -t emeday17/eventos-iam:0.1.0         -f services/iam-service/Dockerfile .
docker build -t emeday17/eventos-catalogo:0.1.0    -f services/catalogo-service/Dockerfile .
docker build -t emeday17/eventos-proveedores:0.1.0 -f services/proveedores-service/Dockerfile .
docker build -t emeday17/eventos-contratacion:0.1.0 -f services/contratacion-service/Dockerfile .




docker push emeday17/eventos-catalogo:0.1.0
docker push emeday17/eventos-iam:0.1.0
docker push emeday17/eventos-contratacion:0.1.0
docker push emeday17/eventos-proveedores:0.1.0






