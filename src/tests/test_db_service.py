import datetime

import pytest

from core.db_service import DBService
from core.db_manager import DBManager
from models.model import Collaborator, Client, Contract, Event


collab_1 = {
    "complet_name": "joe black",
    "email": "joe@gmail.com",
    "phone": "133343",
    "password": "454654",
    "role_id": 1
}

collab_2 = {
    "complet_name": "lisa green",
    "email": "lisa@gmail.com",
    "phone": "65456454",
    "password": "dfs4134ds",
    "role_id": 2
}

collab_3 = {
    "complet_name": "john doo",
    "email": "john@gmail.com",
    "phone": "65346454",
    "password": "ddsfddd34ds",
    "role_id": 3
}

client_1 = {
    "client_name": "client_1",
    "email": "client@gmail.com",
    "phone": "4343434",
    "company": "company",
    "commercial_id": 1,
}

client_2 = {
    "client_name": "client_2",
    "email": "client_2@gmail.com",
    "phone": "4343434",
    "company": "company_2",
    "commercial_id": 1,
}

contract_1 = {
    "client_id": 1,
    "commercial_id": 1,
    "total_cost": 20000,
    "remaining_to_pay": 10000,
    "date": datetime.date(2025, 1, 1),
    "status": False
}

contract_2 = {
    "client_id": 1,
    "commercial_id": 1,
    "total_cost": 20000,
    "remaining_to_pay": 10000,
    "date": datetime.date(2025, 1, 1),
    "status": False
}

event_1 = {
    "contract_id": 1,
    "client_id": 1,
    "event_start": datetime.date(2026, 2, 2),
    "event_end": datetime.date(2026, 2, 20),
    "support_id": 2,
    "location": "chateau la tour",
    "attendees": 200,
    "note": "lorem ipsum"
}

manager = DBManager()


@pytest.fixture
def service():
    session = manager.get_test_session()
    return DBService(session)


class TestBDService:

    @classmethod
    def teardown_class(cls):
        manager.stop_test_session()

    def test_create_and_get_one(self, service):
        service.create(Collaborator, collab_1)
        service.create(Collaborator, collab_2)
        service.create(Client, client_1)
        service.create(Contract, contract_1)
        service.create(Event, event_1)

        res_collab_1 = service.get_one(Collaborator, 1)
        res_collab_2 = service.get_one(Collaborator, 2)
        res_client_1 = service.get_one(Client, 1)
        res_contract_1 = service.get_one(Contract, 1)
        res_event_1 = service.get_one(Event, 1)

        res_collab_1["role_id"] = 1
        res_collab_2["role_id"] = 2
        res_client_1["commercial_id"] = 1
        res_client_1["commercial_id"] = 1

        for field in ["create_date", "update_date"]:
            del res_client_1[field]
        res_contract_1["client_id"] = 1
        res_contract_1["commercial_id"] = 1
        res_event_1["client_id"] = 1
        res_event_1["support_id"] = 2

        collab_1["id"] = 1
        collab_1["role"] = "gestion"
        collab_2["id"] = 2
        collab_2["role"] = "commercial"
        client_1["id"] = 1
        client_1["commercial"] = "joe black"
        contract_1["id"] = 1
        contract_1["client"] = "client_1"
        contract_1["commercial"] = "joe black"
        event_1["id"] = 1
        event_1["client"] = "client_1"
        event_1["support"] = "lisa green"

        assert res_collab_1 == collab_1
        assert res_collab_2 == collab_2
        assert res_client_1 == client_1
        assert res_contract_1 == contract_1
        assert res_event_1 == event_1

    def test_get_all(self, service):
        res = service.get_all(Collaborator)
        assert len(res) == 2

    def test_update(self, service):
        service.create(Client, client_2)
        service.create(Contract, contract_2)

        service.update(
            Collaborator, 1,
            data={"email": "modify@collab.com"}
        )
        service.update(
            Client, 1,
            data={
                "email": "modify@client.com",
                "commercial_id": 2
            }
        )
        service.update(
            Contract, 1,
            data={
                "remaining_to_pay": 500,
                "commercial_id": 2
            }
        )
        service.update(
            Event, 1,
            data={
                "attendees": 300,
                "support_id": 1
            }
        )

        res_collab = service.get_one(Collaborator, 1)
        res_client = service.get_one(Client, 1)
        res_contract = service.get_one(Contract, 1)
        res_event = service.get_one(Event, 1)

        assert res_collab["email"] == "modify@collab.com"
        assert res_client["email"] == "modify@client.com"
        assert res_client["commercial"] == "lisa green"
        assert res_contract["remaining_to_pay"] == 500
        assert res_contract["commercial"] == "lisa green"
        assert res_event["attendees"] == 300
        assert res_event["support"] == "joe black"

    def test_delete(self, service):
        service.create(Collaborator, collab_3)
        service.delete(Collaborator, 3)
        service.delete(Client, 2)
        service.delete(Contract, 2)
        service.delete(Event, 1)

        res_collab = service.get_one(Collaborator, 3)
        res_client = service.get_one(Client, 2)
        res_contract = service.get_one(Contract, 2)
        res_event = service.get_one(Event, 2)

        assert res_collab is None
        assert res_client is None
        assert res_contract is None
        assert res_event is None
