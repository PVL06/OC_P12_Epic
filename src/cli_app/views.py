import re

from rich.table import Table
from rich.console import Console
import msvcrt

INPUT_FIELDS = {
    "gestion": {
        "collaborator": [
            ("name", "Enter complet name: "),
            ("email", "Enter email address: "),
            ("phone", "Enter phone number: "),
            ("password", "Enter password (6 chars minimum): "),
            ("role_id", "Enter collaborator role (1: gestion, 2: commercial, 3: support): ")
        ],
        "contract": [
            ("client_id"),
            ("total_cost", "Enter total cost: "),
            ("remaining_to_pay", "Enter remaining to pay: "),
            ("date", "Enter date (format: dd/mm/yyy): "),
            ("status", "Contract signed? (0: no, 1: yes): ")
        ]
    }
}


class ViewInput:
    def __init__(self):
        self.console = Console()

    def creation_input(self, source, role):
        fields = INPUT_FIELDS[role][source]
        data = {}
        for field in fields:
            loop = True
            while loop:
                value = self.console.input(field[1])
                value = self._check_input(field[0], value)
                if value:
                    data[field[0]] = value
                    loop = False
                else:
                    self.console.print(f"Invalid input for field {field[0]}", style="red")
        return data

    def _check_input(self, field, value):
        if field in ["attendees", "total_cost", "remaining_to_pay"]:
            if value.isdigit():
                return int(value)
        elif field == "phone":
            if value.isdigit():
                return value
        elif field == "password":
            if len(value) >= 6:
                return value
        elif field == "status":
            if value == "0":
                return False
            elif value == "1":
                return True
        elif field == "role_id":
            if value in ["1", "2", "3"]:
                return int(value)
        elif field in ["date", "event_start", "event_end"]:
            pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
            if re.match(pattern, value):
                return value
        elif field == "email":
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if re.match(pattern, value):
                return value
        else:
            return value


class SelectInput:

    UP = b'a'
    DOWN = b'w'
    ENTER = b'\r'
    QUIT = b'q'

    def __init__(self, data: dict, msg: str, select=False, update=False) -> None:
        self.title = list(data.keys())[0]
        self.data = data[self.title]
        self.msg = msg
        self.update = update
        self.select = select if not update else True
        self.pointer = 0
        self.console = Console()

    def _create_table(self) -> Table:
        table = Table(
            title=self.title.capitalize(),
            title_justify="left",
            title_style="black on green"
        )
        for key in list(self.data[0].keys()):
            table.add_column(key)

        for idx, line in enumerate(self.data):
            table.add_row(
                *[str(value) for value in line.values()],
                style="on blue" if idx == self.pointer else ""
            )
        return table

    def _header(self) -> None:
        self.console.clear()
        self.console.print(
            f"\n>>>   {self.msg}   <<<\n",
            style="black on green",
            justify="center"
        )
        validation = "| Enter : ⏎ valid " if self.select else ""
        self.console.print(
            f" Commands   a : ↑ up | w : ↓ down {validation}| q: quit",
            style="black on blue",
            justify="center"
        )
        self.console.print("\n\n")

    def live_show(self) -> int:
        data_len = len(self.data) - 1
        id = None
        loop = True
        while loop:
            self._header()
            self.console.print(self._create_table())
            key = msvcrt.getch()
            match key:
                case self.UP:  # up key
                    if self.pointer == 0:
                        self.pointer = data_len
                    else:
                        self.pointer -= 1

                case self.DOWN:  # down key
                    if self.pointer == data_len:
                        self.pointer = 0
                    else:
                        self.pointer += 1

                case self.ENTER:  # enter key
                    if self.select:
                        selected = self.data[self.pointer]
                        id = int(selected.get("id"))
                        self.console.print(f"Selected id : {id}\n")
                        loop = False
                    else:
                        id = 0

                case self.QUIT:  # q key (quit)
                    loop = False
                case _:
                    pass
        return id
