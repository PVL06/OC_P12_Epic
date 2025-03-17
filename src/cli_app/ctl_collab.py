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
        self.input = ViewInput()

    def request_api(self, route: str, data=None) -> dict | None:
        try:
            if token := self._get_token():
                if data:
                    response = requests.post(
                        url=self.base_url + route,
                        json=data,
                        headers={"Authorization": token}
                    )
                else:
                    response = requests.get(
                        url=self.base_url + route,
                        headers={"Authorization": token}
                    )

                if response.status_code == 200:
                    return response.json()
                else:
                    self.console.print(response.json().get("error"), style="red")
            else:
                self.console.print("You need to log in", style="red")
        except requests.exceptions.ConnectionError:
            self.console.print("Server unavailable", style="red")

    def user_perm(roles: list[str]):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                response = self.request_api("/session")
                if response:
                    if response.get("role") in roles:
                        kwargs["user_role"] = response.get("role")
                        kwargs["user_id"] = response.get("id")
                        return func(self, *args, **kwargs)
                    else:
                        self.console.print("No authorized", style="red")
            return wrapper
        return decorator

    def _get_token(self) -> str | None:
        if os.path.exists(self.token_path):
            with open(self.token_path, mode="r") as file:
                token = file.readline()
            return token


class Collaborator(APIBase):
    def __init__(self):
        super().__init__()

    def login(self, email: str, password: str) -> None:
        try:
            url = self.base_url + "/login"
            response = requests.post(url, json={"email": email, "password": password})
            if response.status_code == 200:
                token = response.json().get("jwt_token")
                with open(self.token_path, mode="w") as file:
                    file.write(token)
                self.console.print(response.json().get("status"), style="green")
            else:
                self.console.print(response.json().get("error"), style="red")
        except requests.exceptions.ConnectionError:
            self.console.print("Server unavailable", style="red")

    def logout(self) -> None:
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.console.print("Deconnected", style="green")

    def get_list(self):
        response = self.request_api("/collab")
        if response:
            select = SelectInput(
                response,
                msg="List of collaborators"
            )
            select.live_show()

    @APIBase.user_perm(["gestion"])
    def create_collab(self, **kwargs) -> None:
        input_data = self.input.creation_input("collaborator", kwargs["user_role"])
        response = self.request_api("/collab/create", input_data)
        if response:
            self.console.print(response["status"], style="green")

    @APIBase.user_perm(["gestion"])
    def update_collab(self, **kwargs) -> None:
        response = self.request_api("/collab")
        if response:
            select = SelectInput(
                response,
                msg="Select collaborator to update",
                select=True
            )
            selected_id = select.live_show()
            print(selected_id)

    @APIBase.user_perm(["gestion"])
    def delete_collab(self, **kwarg) -> None:
        response = self.request_api("/collab")
        if response:
            select = SelectInput(
                response,
                msg="Select collaborator to update",
                select=True
            )
            selected_id = select.live_show()
            if selected_id:
                confirm = Confirm.ask("Are you sure to delete this collaborator")
                if confirm:
                    response = self.request_api(f"/collab/delete/{str(selected_id)}")
                    if response:
                        self.console.print(response["status"], style="green")
                else:
                    self.console.print("operation canceled", style="red")
