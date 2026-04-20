from locust import HttpUser, task, between

class UsuarioHotSale(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def comprar(self):
        # 30% del tráfico intenta comprar y sufre/genera la demora de 3 segundos
        self.client.post("/orders", json={"producto_id": 1, "cantidad": 1})

    @task(7)
    def ver_catalogo(self):
        # 70% del tráfico solo navega, pero sufrirá el impacto
        self.client.get("/products")