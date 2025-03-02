import pytest
from sqlalchemy import select

from database import Database
from models import Collaborator, Client

database = Database()
Session = database.get_test_session()


@pytest.fixture
def collaborator():
    collaborator = Collaborator(
        complet_name="John Collab",
        email="John@gmail.com",
        phone="0785056255",
        password="mjkfdqmgmq"
    )
    return collaborator


class TestDatabase:

    @classmethod
    def teardown_class(cls):
        database.stop_test_session()

    def test_add_new_collaborator(self, collaborator):
        with Session() as session:
            session.add(collaborator)
            session.commit()
            stmt = select(Collaborator).where(Collaborator.id == 1)
            assert session.scalars(stmt).one() == collaborator

    def test_add_new_client(self):
        with Session() as session:
            stmt = select(Collaborator).where(Collaborator.id == 1)
            collaborator = session.scalar(stmt)

            client = Client(
                client_name="John Client",
                email="John@gmail.com",
                phone="0785056255",
                company="Client company",
                commercial_id=collaborator.id
            )
            session.add(client)
            stmt = select(Client).where(Client.id == 1)
            assert session.scalars(stmt).one() == client
