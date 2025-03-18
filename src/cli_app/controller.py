import os
import requests

from rich.console import Console
from rich.prompt import Confirm

from cli_app.views import ViewInput, ViewSelect


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

    def update_field(self, route: str, data: dict, id: int) -> None:
        loop = True
        while loop:
            select = ViewSelect(
                data,
                msg="Chose field to update",
                update=True
            )
            field = select.live_show(id)
            if field:
                value = self.console.input(f"{field[0]} ({field[1]}): ")
                valid_value = self.input.check_input(field[0], value)
                if valid_value is not None:
                    data = self.request_api(
                                f"{route}/update/{id}",
                                data={field[0]: valid_value}
                            )
                else:
                    self.console.print(f"Invalid input for field {field[0]}", style="red")
                confirm = Confirm.ask("Update another field")
                if confirm:
                    data = self.request_api(route)
                    if not data:
                        loop = False
                else:
                    loop = False
            else:
                loop = False

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
        response = self.request_api("/collab")  # filter by role
        if response.get("collaborators"):
            select = ViewSelect(
                response,
                msg="List of collaborators"
            )
            select.live_show()
        else:
            self.console.print("No collaborator", style="red")

    @APIBase.user_perm(["gestion"])
    def create_collab(self, **kwargs) -> None:
        input_data = self.input.creation_input("collaborator", kwargs["user_role"])
        response = self.request_api("/collab/create", input_data)
        if response:
            self.console.print(response["status"], style="green")

    @APIBase.user_perm(["gestion"])
    def update_collab(self, **kwargs) -> None:
        loop = True
        while loop:
            collabs = self.request_api("/collab")  # filter by role
            if collabs:
                select = ViewSelect(
                    collabs,
                    msg="Select collaborator to update",
                    select=True
                )
                collab_id = select.live_show()
                if collab_id:
                    self.update_field(route="/collab", data=collabs, id=collab_id)
                else:
                    loop = False
            else:
                loop = False

    @APIBase.user_perm(["gestion"])
    def delete_collab(self, **kwarg) -> None:
        collabs = self.request_api("/collab")
        if collabs:
            select = ViewSelect(
                collabs,
                msg="Select collaborator to update",
                select=True
            )
            collab_id = select.live_show()
            if collab_id:
                confirm = Confirm.ask("Are you sure to delete this collaborator")
                if confirm:
                    response = self.request_api(f"/collab/delete/{str(collab_id)}")
                    if response:
                        self.console.print(response["status"], style="green")
                else:
                    self.console.print("operation canceled", style="red")


class Client(APIBase):
    def __init__(self):
        super().__init__()

    def get_list(self):
        response = self.request_api("/client")  # filter commercial client
        if response.get("clients"):
            select = ViewSelect(
                response,
                msg="List of clients"
            )
            select.live_show()
        else:
            self.console.print("No client", style="red")

    @APIBase.user_perm(["commercial"])
    def create_client(self, **kwargs):
        input_data = self.input.creation_input("client", kwargs["user_role"])
        response = self.request_api("/client/create", input_data)
        if response:
            self.console.print(response["status"], style="green")

    @APIBase.user_perm(["commercial"])
    def update_client(self, **kwargs):
        loop = True
        while loop:
            clients = self.request_api("/client")  # filter commercial client
            if clients:
                select = ViewSelect(
                    clients,
                    msg="Select client to update",
                    select=True
                )
                client_id = select.live_show()
                if client_id:
                    self.update_field(route="/client", data=clients, id=client_id)
                else:
                    loop = False
            else:
                loop = False


class Contract(APIBase):
    def __init__(self):
        super().__init__()

    def get_list(self):
        contracts = self.request_api("/contract")  # filter by client and by positive remaining to pay
        if contracts.get("contracts"):
            select = ViewSelect(
                contracts,
                msg="List of contract"
            )
            select.live_show()
        else:
            self.console.print("No contract", style="red")

    @APIBase.user_perm(["gestion"])
    def create_contract(self, **kwargs):
        clients = self.request_api("/client")  # filter commercial client
        if clients:
            select = ViewSelect(
                clients,
                msg="Select the client for the new contract",
                select=True
            )
            client_id = select.live_show()
            if client_id:
                input_data = self.input.creation_input("contract", kwargs["user_role"])
                input_data.update({"client_id": client_id})
                response = self.request_api("/contract/create", input_data)
                if response:
                    self.console.print(response["status"], style="green")

    @APIBase.user_perm(["gestion", "commercial"])
    def update_contract(self, **kwargs):
        loop = True
        while loop:
            contracts = self.request_api("/contract")  # filter if commercial (contract from commercial client)
            if contracts:
                select = ViewSelect(
                    contracts,
                    msg="Select contract to update",
                    select=True
                )
                contract_id = select.live_show()
                if contract_id:
                    self.update_field(route="/contract", data=contracts, id=contract_id)
                else:
                    loop = False
            else:
                loop = False


class Event(APIBase):
    def __init__(self):
        super().__init__()

    def get_list(self):
        events = self.request_api("/event")  # add filter for event with no support, by client, by support event
        if events.get("events"):
            select = ViewSelect(
                events,
                msg="List of events"
            )
            select.live_show()
        else:
            self.console.print("No event", style="red")

    @APIBase.user_perm(["commercial"])
    def create_event(self, **kwargs):
        contracts = self.request_api("/contract")  # filter only contract for commercial client
        if contracts:
            select = ViewSelect(
                contracts,
                msg="Select contact for this event",
                select=True
            )
            contract_id = select.live_show()
            if contract_id:
                input_data = self.input.creation_input("event", kwargs["user_role"])
                input_data.update({"contract_id": contract_id})
                response = self.request_api("/event/create", input_data)
                if response:
                    self.console.print(response["status"], style="green")

    @APIBase.user_perm(["gestion", "support"])
    def update_event(self, **kwargs):
        loop = True

        if kwargs["user_role"] == "gestion":
            while loop:
                events = self.request_api("/event")  # possible to add filter -> event with no support
                supports = self.request_api("/collab")  # filter only support collaborator
                if events and supports:
                    select = ViewSelect(
                        events,
                        msg="Select event to update",
                        select=True
                    )
                    event_id = select.live_show()
                    select = ViewSelect(
                        supports,
                        msg="Select support for this event",
                        select=True
                    )
                    support_id = select.live_show()
                    if event_id and support_id:
                        self.request_api(
                            f"/event/update/{event_id}",
                            data={"support_id": support_id}
                        )
                    else:
                        loop = False
                else:
                    loop = False

        elif kwargs["user_role"] == "support":
            while loop:
                events = self.request_api("/event")  # filter only support event
                if events:
                    select = ViewSelect(
                        events,
                        msg="Select event to update",
                        select=True
                    )
                    event_id = select.live_show()
                    if event_id:
                        self.update_field(route="/event", data=events, id=event_id)
                    else:
                        loop = False
                else:
                    loop = False
