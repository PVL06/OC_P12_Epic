import os

import pytest
from unittest.mock import MagicMock

from cli_app.controller import APIBase, Collaborator, Client, Contract, Event


@pytest.fixture
def api_base():
    base = APIBase()
    base.base_url = "http://fake_url.com"
    return base


@pytest.fixture
def api_collab():
    collab = Collaborator()
    return collab


@pytest.fixture
def api_client():
    client = Client()
    return client


@pytest.fixture
def api_contract():
    contract = Contract()
    return contract


@pytest.fixture
def api_event():
    event = Event()
    return event


class TestAPIBase:

    def test_get_and_post_request_api_with_token(self, mocker, api_base):
        mocker.patch("cli_app.controller.APIBase._get_token", return_value="fake token")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}

        mocker.patch("cli_app.controller.requests.get", return_value=mock_response)
        mocker.patch("cli_app.controller.requests.post", return_value=mock_response)

        res_get = api_base.request_api("/test")
        res_post = api_base.request_api("/test", data={"some": "data"})
        assert res_get == {"status": "success"}
        assert res_post == {"status": "success"}

    def test_request_api_without_token(self, mocker, capsys, api_base):
        mocker.patch("cli_app.controller.APIBase._get_token", return_value=None)

        api_base.request_api("/test")
        captured = capsys.readouterr()
        assert "You need to log in" in captured.out

    def test_request_api_error_response(self, mocker, capsys, api_base):
        mocker.patch("cli_app.controller.APIBase._get_token", return_value="fake token")
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "error response"}

        mocker.patch("cli_app.controller.requests.get", return_value=mock_response)

        api_base.request_api("/test")
        captured = capsys.readouterr()
        assert "error response" in captured.out


class TestCollaborator:

    def test_login_with_valid_email_and_passsword(self, mocker, capsys, api_collab):
        token_path = os.path.join(os.getcwd(), "token")
        if os.path.exists(token_path):
            os.remove(token_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "jwt_token": "token test"}

        mocker.patch("cli_app.controller.requests.post", return_value=mock_response)

        api_collab.login(email="test@test.com", password="1234")
        captured = capsys.readouterr()

        assert "success" in captured.out
        assert os.path.exists(token_path)

    def test_login_with_invalid_email_and_passsword(self, mocker, capsys, api_collab):
        token_path = os.path.join(os.getcwd(), "token")
        if os.path.exists(token_path):
            os.remove(token_path)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid"}

        mocker.patch("cli_app.controller.requests.post", return_value=mock_response)

        api_collab.login(email="test@test.com", password="1234")
        captured = capsys.readouterr()

        assert "invalid" in captured.out
        assert not os.path.exists(token_path)

    def test_logout(self, api_collab):
        token_path = os.path.join(os.getcwd(), "token")
        with open(token_path, "w") as file:
            file.write("test token")
        api_collab.logout()
        assert not os.path.exists(token_path)

    def test_get_with_no_collab(self, mocker, capsys, api_collab):
        mocker.patch("cli_app.controller.Collaborator.request_api", return_value={"collaborators": []})
        api_collab.get_list()
        captured = capsys.readouterr()

        assert "No collaborator" in captured.out


class TestWork:

    def test_get_client_with_no_client(self, mocker, capsys, api_client):
        mocker.patch("cli_app.controller.Client.request_api", return_value={"clients": []})
        api_client.get_list()
        captured = capsys.readouterr()

        assert "No client" in captured.out

    def test_get_contract_with_no_contract(self, mocker, capsys, api_contract):
        mocker.patch("cli_app.controller.Contract.request_api", return_value={"contracts": []})
        api_contract.get_list()
        captured = capsys.readouterr()

        assert "No contract" in captured.out

    def test_get_event_with_no_event(self, mocker, capsys, api_event):
        mocker.patch("cli_app.controller.Event.request_api", return_value={"events": []})
        api_event.get_list()
        captured = capsys.readouterr()

        assert "No event" in captured.out