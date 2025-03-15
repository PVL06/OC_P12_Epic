import os
import requests

from rich.console import Console

base_url = "http://127.0.0.1:8000/"
console = Console()


class APIBase:

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/"
        self.token_path = os.path.join(os.getcwd(), "token")
        self.console = Console()

    def get(self, route):
        try:
            if token := self._get_token():
                res = requests.get(
                    url=self.base_url + route,
                    headers={"Authorization": token}
                )
                return res
            else:
                self.console.print("No connected", style="red")
        except requests.exceptions.ConnectionError:
            print("Server unavailable")

    def post(self, route, data):
        try:
            if token := self._get_token():
                res = requests.post(
                    url=self.base_url + route,
                    json=data,
                    headers={"Authorization": token}
                )
            else:
                self.console.print("No connected", style="red")
        except requests.exceptions.ConnectionError:
            print("Server unavailable")
        else:
            return res

    def _get_token(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, mode="r") as file:
                token = file.readline()
            return token


class Collaborator(APIBase):
    def __init__(self):
        super().__init__()

    def login(self, email, password):
        try:
            url = self.base_url + "/login"
            res = requests.post(url, json={"email": email, "password": password})
            if res.status_code == 200:
                msg = res.json()
                if msg.get("error"):
                    console.print(msg["error"], style="red")
                else:
                    token = msg.get("jwt_token")
                    with open(self.token_path, mode="w") as file:
                        file.write(token)
                    console.print(msg["status"], style="green")
            else:
                print("Internal error")
        except requests.exceptions.ConnectionError:
            print("Server unavailable")

    def logout(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        console.print("Deconnected", style="green")

    def get_list(self):
        data = self.get("/collab")
        if data:
            console.print(data.json())
