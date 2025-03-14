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
        "phone": "12345678",
        "password": "1234",
        "role_id": 2
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
            "Authorization": "Bearer " + res.json().get("jwt_token")
        }
        return header

    # Tests for collaborator login

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
        assert res.status_code == 200
        assert res.json() == {"error": "email invalid !"}

    def test_login_with_invalid_password(self, client):
        url = base_url + "/login"
        data = {
            "email": "epic@epic.com",
            "password": "12345"
        }
        res = client.post(url, json=data)
        assert res.status_code == 200
        assert res.json() == {"error": "Invalid password !"}

    # Tests for get collaborators and authorization with jwt token header

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
            "Authorization": "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
        }
        res = client.get(url, headers=header)
        assert res.status_code == 401
        assert res.json() == {"error": "Invalid token"}

    # Tests for create collaborator and for role permissions

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

    # Tests for update collaborator and for fields type validator and fields permission

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
        assert res.status_code == 200
        assert res.json() == {"error": "Invalid field: address"}

    def test_update_collaborator_with_invalid_value(self, client, gestion_user):
        url = base_url + "/collab/update/1"
        res = client.post(
            url,
            json={"phone": 22222222},
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {"error": "Invalid value for field: phone"}

    # tests for delete collaborator and check invalid id in url

    def test_delete_collaborator_with_invalid_url_id(self, client, gestion_user):
        url = base_url + "/collab/delete/3"
        res = client.get(
            url,
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {'error': 'Invalid collaborator id'}

    def test_delete_collaborator_with_valid_url_id(self, client, gestion_user):
        url = base_url + "/collab/delete/2"
        res = client.get(
            url,
            headers=self._header_with_auth(client, gestion_user)
        )
        assert res.status_code == 200
        assert res.json() == {"status": "Collaborator deleted"}
