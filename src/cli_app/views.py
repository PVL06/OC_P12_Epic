import re

from rich.table import Table
from rich.console import Console
import msvcrt

ROLE_FIELDS = {
    "gestion": {
        "collaborator": ["name", "email", "phone", "password", "role_id"],
        "contract": ["event_title", "total_cost", "remaining_to_pay", "date", "status"],
        "event": []
    },
    "commercial": {
        "client": ["name", "email", "phone", "company"],
        "contract": ["total_cost", "total_cost", "remaining_to_pay", "status"],
        "event": ["event_start", "event_end", "location", "attendees", "note"]
    },
    "support": {
        "event": ["event_start", "event_end", "location", "attendees", "note"]
    }
}

FIELDS_PROMPT = {
    "name": "Enter name (lastname & firstname): ",
    "email": "Enter email address: ",
    "phone": "Enter phone number: ",
    "password": "Enter password (6 chars minimum): ",
    "total_cost": "Enter total cost: ",
    "role_id": "Enter collaborator role (1: gestion, 2: commercial, 3: support): ",
    "event_title": "Enter the name of event for this contract: ",
    "remaining_to_pay": "Enter remaining to pay: ",
    "date": "Enter date (format: dd/mm/yyy): ",
    "event_start": "Enter event start date and hour (format: dd/mm/yyyy hh:mm): ",
    "event_end": "Enter event end date and hour (format: dd/mm/yyyy hh:mm): ",
    "status": "Contract signed? (0: no, 1: yes): ",
    "company": "Enter company name: ",
    "location": "Enter event location for this event: ",
    "attendees": "Enter attendees number for this event: ",
    "note": "Enter note for this event: "
}


class ViewInput:
    def __init__(self):
        self.console = Console()

    def creation_input(self, source: str, role: str) -> dict:
        valid_fields = ROLE_FIELDS[role][source]
        data = {}
        for field in valid_fields:
            loop = True
            while loop:
                value = self.console.input(FIELDS_PROMPT[field])
                value = self.check_input(field, value)
                if value is not None:
                    data[field] = value
                    loop = False
                else:
                    self.console.print(f"Invalid input for field {field}", style="red")
        return data

    def check_input(self, field: str, value: str):
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
        elif field == "date":
            pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
            if re.match(pattern, value):
                return value
        elif field in ["event_start", "event_end"]:
            pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(20[2-9][0-9]) ([01][0-9]|2[0-3]):([0-5][0-9])$"
            if re.match(pattern, value):
                return value
        elif field == "email":
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if re.match(pattern, value):
                return value
        else:
            return value


class ViewSelect:

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
            title=f" {self.title.capitalize()}",
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

    def _create_item_table(self) -> Table:
        table = Table()
        table.add_column("Field")
        table.add_column("Value")
        for idx, (key, value) in enumerate(self.data):
            table.add_row(
                key,
                str(value),
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

    def live_show(self, id=None) -> int:
        if id and self.update:
            for row in self.data:
                if row.get("id") == id:
                    self.data = [item for item in row.items() if item[0] in FIELDS_PROMPT.keys()]
                    break

        data_len = len(self.data) - 1
        loop = True
        while loop:
            self._header()
            if self.update:
                self.console.print(self._create_item_table())
            else:
                self.console.print(self._create_table())
            key = msvcrt.getch()
            match key:
                case self.UP:
                    if self.pointer == 0:
                        self.pointer = data_len
                    else:
                        self.pointer -= 1

                case self.DOWN:
                    if self.pointer == data_len:
                        self.pointer = 0
                    else:
                        self.pointer += 1

                case self.ENTER:
                    if self.select:
                        if self.update:
                            return self.data[self.pointer]
                        else:
                            item_id = self.data[self.pointer].get("id")
                            return int(item_id)

                case self.QUIT:
                    return None
                case _:
                    pass
