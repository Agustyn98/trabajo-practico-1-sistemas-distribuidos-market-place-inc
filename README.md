# 3: Código FastAPI del monolito + Tests de carga

El problema:

- El sistema tiene una base de datos unica con un limite de 15 conexiones

- POST /orders ocupa la conexion por al menos 3 segundos

## Instrucciones
1. `pip install -r requirements.txt`
2. `uvicorn main:app --reload`
3. `locust -f locustfile.py --headless -u 50 -r 5 --host http://localhost:8000`

## Resultados
Durante la ejecución de Locust con 50 usuarios concurrentes, se observó el siguiente comportamiento que demuestra el problema central del monolito:

El endpoint `POST /orders` demora 3 segundos simulando un procesador de pagos externo.

Aunque `GET /products` es una consulta simple, los tiempos de respuesta se incrementan cuanto mas carga hay, esto ocurre porque comparte los recursos de la misma base de datos con el módulo de pedidos.

Ademas, debido al limite de 15 usuarios, las peticiones empiezan a fallar despues de unos segundos.