from starlette.testclient import TestClient
import pytest
from unittest.mock import MagicMock

from server_epic import app


base_url = "http://127.0.0.1:8000"


class TestApi:

    def test_get_collab_without_jwt_token(self):
        url = base_url + "/collab"
        client = TestClient(app)
        res = client.get(url)
        assert res.status_code == 401
