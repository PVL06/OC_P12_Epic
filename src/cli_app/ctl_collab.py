import os
import requests

from rich.console import Console
from rich.prompt import Confirm

from cli_app.views import ViewInput, SelectInput

base_url = "http://127.0.0.1:8000/"


class APIBase:

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/"
        self.token_path = os.path.join(os.getcwd(), "token")
        self.console = Console()

    def get_api(self, route):
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

    def post_api(self, route, data):
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
        self.input = ViewInput()

    def login(self, email, password):
        try:
            url = self.base_url + "/login"
            res = requests.post(url, json={"email": email, "password": password})
            if res.status_code == 200:
                msg = res.json()
                if msg.get("error"):
                    self.console.print(msg["error"], style="red")
                else:
                    token = msg.get("jwt_token")
                    with open(self.token_path, mode="w") as file:
                        file.write(token)
                    self.console.print(msg["status"], style="green")
            else:
                print("Internal error")
        except requests.exceptions.ConnectionError:
            print("Server unavailable")

    def logout(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.console.print("Deconnected", style="green")

    def get_list(self):
        res = self.get_api("/collab").json()
        if res.get("collaborators"):
            select = SelectInput(
                res,
                msg="List of collaborators"
            )
            select.live_show()
        else:
            self.console.print(res.get("error"), style="red")

    def create_collab(self):
        res = self.get_api("/session")
        user_role = res.json().get("role")
        if user_role == "gestion":
            data = self.input.creation_input("collaborator", user_role)
            res = self.post_api("/collab/create", data)
            if res.status_code == 200:
                decode_res = res.json()
                if decode_res.get("status"):
                    self.console.print(decode_res["status"], style="green")
                else:
                    self.console.print(decode_res["error"], style="red")
        else:
            self.console.print("No authorized", style="red")

    def update_collab(self):
        res = self.get_api("/collab")
        if res.status_code == 200:
            select = SelectInput(
                res.json(),
                msg="Select collaborator to update",
                select=True
            )
            selected_id = select.live_show()

    def delete_collab(self):
        res = self.get_api("/collab").json()
        if res.get("collaborators"):
            select = SelectInput(
                res,
                msg="Select collaborator to update",
                select=True
            )
            selected_id = select.live_show()
            if selected_id:
                confirm = Confirm.ask("Are you sure to delete this collaborator")
                if confirm:
                    res = self.get_api(f"/collab/delete/{str(selected_id)}").json()
                    if res.get("status"):
                        self.console.print(res["status"], style="green")
                    else:
                        self.console.print(res.get("error") + "\n", style="red")
        else:
            self.console.print(res.get("error"))
