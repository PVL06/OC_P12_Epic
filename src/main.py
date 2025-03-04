from models.model import Client, Collaborator
from core.db_service import DBService

collab = {
    "complet_name": "joe l'indien",
    "email": "joe@gmail.com",
    "phone": "456454555",
    "password": "fdsmlkmd44"
}

ctl = DBService()

"""
"""
print("\n=== create collab ===")
collab = {
    "complet_name": "joe",
    "email": "joe@gmail.com",
    "phone": "133343",
    "password": "454654"
}
ctl.create(Collaborator, collab)
collab = ctl.get_one(Collaborator, 1)
print(collab)

print("\n=== create client ===")
client = {
    "client_name": "client name",
    "email": "client@gmail.com",
    "phone": "4343434",
    "company": "company",
    "commercial_id": collab["id"]
}
ctl.create(Client, client)
clients = ctl.get_all(Client)
print(clients)
"""
print("\n=== delete client ===")
delete = ctl.delete(Client, 1)
print(delete)
"""

print("\n=== clients all===")
clients = ctl.get_all(Client)
print(clients)

print("\n=== collabs all ===")
clients = ctl.get_all(Collaborator)
print(clients)

print("\n=== clients all===")
clients = ctl.get_all(Client)
print(clients)

print("\n=== modify client ===")
check = ctl.update(Client, 1, {"commercial_id": 1})
print(check)

print("\n=== clients all===")
clients = ctl.get_all(Client)
print(clients)

print("=== client one id 1 ===")
client = ctl.get_one(Client, 2)
print(client)
