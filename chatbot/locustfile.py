from locust import HttpUser, task, between
import random

messages = [
    "cuando abre el comedor universitario?",
    "que deportes puedo practicar?",
    "como me inscribo a una beca?",
    "a que hora hay futbol?",
]

class RasaBotUser(HttpUser):
    wait_time = between(10, 15)  # tiempo entre consultas

    @task
    def send_message(self):
        msg = random.choice(messages)
        self.client.post("/webhooks/rest/webhook", json={"sender": str(random.randint(1, 9999)), "message": msg})
