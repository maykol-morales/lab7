from locust import HttpUser, task, between

MOCKOON_URL = "http://localhost:3001/paper"

class MyUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def create_paper(self):
        response = self.client.get(MOCKOON_URL, name="GET /paper (Mockoon)")
        paper = response.json()

        self.client.post(
            "/papers/",
            json=paper,
            name="POST /papers/"
        )
