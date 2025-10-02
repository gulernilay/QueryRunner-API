# Performance test dosyası

from locust import HttpUser, task, between

class QueryRunnerUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/")

    @task
    def login_and_query(self):
        response = self.client.post("/auth/login", json={"username":"test", "password":"123"})
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.client.post("/query/", json=["some_key"], headers={"Authorization": f"Bearer {token}"})

            