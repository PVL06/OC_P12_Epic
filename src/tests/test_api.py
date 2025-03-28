import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette

from server.api_collab import CollabAPI
from server.api_work import ClientAPI, ContractAPI, EventAPI
from server.db_manager import DBManager
from server.middlewares import JWTMiddleware, DatabaseMiddleware


manager = DBManager()
base_url = "http://127.0.0.1:8000"


def create_test_app():
    api_routes = [
        CollabAPI.get_routes(),
        ClientAPI.get_routes(),
        ContractAPI.get_routes(),
        EventAPI.get_routes()
    ]

    all_routes = []
    for routes in api_routes:
        all_routes.extend(routes)

    app = Starlette(
        debug=True,
        routes=all_routes
    )

    app.add_middleware(JWTMiddleware)
    app.add_middleware(DatabaseMiddleware, testing=True)
    return app


@pytest.fixture(scope="class")
def client():
    client = TestClient(create_test_app())
    yield client
    client.close()


@pytest.fixture
def gestion_user():
    return {
        "email": "epic@epic.com",
        "password": "epic&1234"
    }


@pytest.fixture
def commercial_user():
    return {
        "name": "collab 1",
        "email": "collab1@gmail.com",
        "phone": "11111111",
        "password": "123456",
        "role_id": 2
    }


@pytest.fixture
def support_user():
    return {
        "name": "support 1",
        "email": "support1@gmail.com",
        "phone": "222222222",
        "password": "123456",
        "role_id": 3
    }


@pytest.fixture
def client_data():
    return {
        "name": "client 1",
        "email": "client1@gmail.com",
        "phone": "4546546",
        "company": "client1 company"
    }


@pytest.fixture
def contract_data():
    return {
        "client_id": 1,
        "total_cost": 2000,
        "remaining_to_pay": 500,
        "date": "02/01/2025",
        "status": False
    }


@pytest.fixture
def event_data():
    return {
        "contract_id": 1,
        "event_start": "25/01/2026 15:30",
        "event_end": "30/01/2026 18:00",
        "support_id": 1,
        "location": "chateau du baron",
        "attendees": 200,
        "note": "lorem ipsum"
    }


class TestApi:

    @classmethod
    def setup_class(cls):
        manager.init_test_database()

    @classmethod
    def teardown_class(cls):
        manager.stop_test_db()

    def _header_with_auth(self, client, user):
        url = base_url + "/login"
        credential = {
            "email": user.get("email"),
            "password": user.get("password")
        }
        res = client.post(url, json=credential)
        header = {
            "Authorization": res.json().get("jwt_token")
        }
        return header

    # _____Tests for collaborator login_____

    def test_login_with_valid_credential(self, client, gestion_user):
        url = base_url + "/login"
        res = client.post(url, json=gestion_user)
        res_data = res.json()
        assert res.status_code == 200
        assert res_data.get("status") == "Connected"
        assert res_data.get("jwt_token") is not None

    def test_login_with_invalid_email(self, client):
        url = base_url + "/login"
        data = {
            "email": "invalid@email.com",
            "password": "1234"
        }
        res = client.post(url, json=data)
        assert res.status_code == 400
        assert res.json() == {"error": "email invalid !"}

    def test_login_with_invalid_password(self, client):
        url = base_url + "/login"
        data = {
            "email": "epic@epic.com",
            "password": "12345"
        }
        res = client.post(url, json=data)
        assert res.status_code == 400
        assert res.json() == {"error": "Invalid password !"}

    # _____Tests for get collaborators and authorization with jwt token header_____

    def test_get_collaborator_with_valid_token(self, client, gestion_user):
        url = base_url + "/collab"
        res = client.get(
            url,
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json().get("collaborators") is not None

    def test_get_collaborator_without_jwt_token(self, client):
        url = base_url + "/collab"
        res = client.get(url)
        assert res.status_code == 401
        assert res.json() == {"error": "No connected !"}

    def test_get_collaborator_with_invalid_jwt_token(self, client):
        url = base_url + "/collab"
        header = {
            "Authorization": "Bearer " + (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0."
                "KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30")
        }
        res = client.get(url, headers=header)
        assert res.status_code == 401
        assert res.json() == {"error": "Invalid token"}

    # _____Tests for create collaborator and for role permissions_____

    def test_create_new_collab_with_valid_role(self, client, gestion_user, commercial_user):
        url = base_url + "/collab/create"
        res = client.post(
            url,
            json=commercial_user,
            headers=self._header_with_auth(client, gestion_user)
        )
        res_data = res.json()
        assert res.status_code == 200
        assert res_data.get("status") == "New collaborator created"

    def test_create_new_collab_with_invalid_role(self, client, commercial_user):
        url = base_url + "/collab/create"
        res = client.post(
            url,
            json=commercial_user,
            headers=self._header_with_auth(client, commercial_user)
        )
        assert res.status_code == 401
        assert res.json() == {"error": "Unauthorized"}

    # _____Tests for update collaborator and for fields type validator and fields permission_____

    def test_update_collaborator_with_valid_fields_and_value(self, client, gestion_user):
        url = base_url + "/collab/update/1"
        res = client.post(
            url,
            json={
                "phone": "22222222"
            },
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Collaborator updated"}

    def test_update_collaborator_with_invalid_field(self, client, gestion_user):
        url = base_url + "/collab/update/1"
        res = client.post(
            url,
            json={"address": "lorem ipsum"},
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 400
        assert res.json() == {"error": "Invalid field: address"}

    def test_update_collaborator_with_invalid_value(self, client, gestion_user):
        url = base_url + "/collab/update/1"
        res = client.post(
            url,
            json={"phone": 22222222},
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 400
        assert res.json() == {"error": "Invalid value for field: phone"}

    # _____Tests for delete collaborator and check invalid id in url_____

    def test_delete_collaborator_with_invalid_url_id(self, client, gestion_user):
        url = base_url + "/collab/delete/3"
        res = client.get(
            url,
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 400
        assert res.json() == {'error': 'Invalid collaborator id'}

    def test_delete_collaborator_with_valid_url_id(self, client, gestion_user):
        url = base_url + "/collab/delete/2"
        res = client.get(
            url,
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Collaborator deleted"}

    # _____Test for client_____

    def test_create_new_client(self, client, gestion_user, commercial_user, client_data):
        # recreate commercial collaborator
        self.test_create_new_collab_with_valid_role(client, gestion_user, commercial_user)

        url = base_url + "/client/create"
        res = client.post(
            url,
            json=client_data,
            headers=self._header_with_auth(client, commercial_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Client created"}

    def test_get_client(self, client, commercial_user):
        url = base_url + "/client"
        res = client.get(
            url,
            headers=self._header_with_auth(client, commercial_user)
            )
        assert res.status_code == 200
        assert len(res.json().get("clients")) == 1

    def test_update_client(self, client, commercial_user):
        url = base_url + "/client/update/1"
        res = client.post(
            url,
            json={"company": "new name company"},
            headers=self._header_with_auth(client, commercial_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Client updated"}

    # _____Test for contract_____

    def test_create_new_contract(self, client, gestion_user, contract_data):
        url = base_url + "/contract/create"
        res = client.post(
            url,
            json=contract_data,
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "contract created"}

    def test_get_contract(self, client, commercial_user):
        url = base_url + "/contract"
        res = client.get(
            url,
            headers=self._header_with_auth(client, commercial_user)
            )
        assert res.status_code == 200
        assert len(res.json().get("contracts")) == 1

    def test_update_contract(self, client, commercial_user):
        url = base_url + "/contract/update/1"
        res = client.post(
            url,
            json={"status": True},
            headers=self._header_with_auth(client, commercial_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Contract updated"}

    # _____Test for event_____

    def test_create_new_event(self, client, commercial_user, event_data):
        url = base_url + "/event/create"
        res = client.post(
            url,
            json=event_data,
            headers=self._header_with_auth(client, commercial_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Event created"}

    def test_get_event(self, client, commercial_user):
        url = base_url + "/event"
        res = client.get(
            url,
            headers=self._header_with_auth(client, commercial_user)
            )
        assert res.status_code == 200
        assert len(res.json().get("events")) == 1

    def test_update_event_support_by_gestion(self, client, gestion_user, support_user):
        # create support user
        url = base_url + "/collab/create"
        res = client.post(
            url,
            json=support_user,
            headers=self._header_with_auth(client, gestion_user)
        )
        res_data = res.json()
        assert res.status_code == 200
        assert res_data.get("status") == "New collaborator created"

        url = base_url + "/event/update/1"
        res = client.post(
            url,
            json={"support_id": 4},
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Event updated"}

    def test_update_event_by_support(self, client, support_user):
        url = base_url + "/event/update/1"
        res = client.post(
            url,
            json={"attendees": 1000},
            headers=self._header_with_auth(client, support_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Event updated"}
