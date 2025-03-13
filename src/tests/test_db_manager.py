import datetime

import pytest
from sqlalchemy import select

from server.db_manager import DBManager
from server.models import Collaborator, Client, Contract, Event

database = DBManager()
Session = database.get_test_session()


@pytest.fixture
def collaborator():
    collaborator = Collaborator(
        name="John Collab",
        email="John@gmail.com",
        phone="0785056255",
        password="mjkfdqmgmq",
        role_id=1
    )
    return collaborator


class TestDatabase:

    @classmethod
    def teardown_class(cls):
        database.stop_test_session()

    def test_add_new_collaborator(self, collaborator):
        with Session.begin() as session:
            session.add(collaborator)
            stmt = select(Collaborator).where(Collaborator.id == 1)
            assert session.scalar(stmt) == collaborator

    def test_add_new_client(self):
        with Session.begin() as session:
            stmt = select(Collaborator).where(Collaborator.id == 1)
            collaborator = session.scalar(stmt)

            client = Client(
                name="John Client",
                email="John@gmail.com",
                phone="0785056255",
                company="Client company",
                commercial_id=collaborator.id
            )
            session.add(client)
            stmt = select(Client).where(Client.id == 1)
            assert session.scalar(stmt) == client

    def test_add_new_contract(self):
        with Session.begin() as session:
            stmt = select(Collaborator).where(Collaborator.id == 1)
            collaborator = session.scalar(stmt)
            stmt = select(Client).where(Client.id == 1)
            client = session.scalar(stmt)
            contract = Contract(
                client_id=client.id,
                commercial_id=collaborator.id,
                total_cost=1200,
                remaining_to_pay=500,
                date=datetime.date(2025, 12, 2),
                status=False
            )
            session.add(contract)
            stmt = select(Contract).where(Contract.id == 1)
            assert session.scalar(stmt) == contract

    def test_add_new_event(self):
        with Session.begin() as session:
            stmt = select(Contract).where(Contract.id == 1)
            contract = session.scalar(stmt)
            stmt = select(Client).where(Client.id == 1)
            client = session.scalar(stmt)
            stmt = select(Collaborator).where(Collaborator.id == 1)
            support = session.scalar(stmt)

            event = Event(
                contract_id=contract.id,
                client_id=client.id,
                event_start=datetime.date(2026, 2, 1),
                event_end=datetime.date(2026, 2, 5),
                support_id=support.id,
                location="chateau de beaulieu",
                attendees=200,
                note="""
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ac nisi et libero cursus feugiat.
                Integer tristique, arcu nec posuere varius, elit nunc pulvinar eros,
                non dapibus lorem eros at nisi. Donec vehicula, risus non gravida tincidunt,
                elit lorem gravida risus, eget tincidunt purus erat nec nunc.
                """
            )
            session.add(event)
            stmt = select(Event).where(Event.id == 1)
            assert session.scalar(stmt) == event
