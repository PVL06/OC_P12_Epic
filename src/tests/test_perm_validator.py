import pytest

from server.utils import check_permission_and_data


class Contract:
    __tablename__ = "contract"


class Collaborator:
    __tablename__ = "collaborator"


@pytest.fixture
def contract_input():
    return {
        "total_cost": 1000,
        "remaining_to_pay": 200,
        "date": "01/01/2021",
        "status": False
    }


class TestPremissionsAndValidator:

    def test_valid_role_in_model_class(self, contract_input):
        res = check_permission_and_data(
            Contract,
            contract_input,
            role="commercial"
        )
        assert res == contract_input

    def test_invalid_role_in_model_class(self, contract_input):
        res = check_permission_and_data(
            Contract,
            contract_input,
            role="support"
        )
        assert res is None

    def test_field_not_in_list(contract_input):
        bad_input = {"test": "test"}
        res = check_permission_and_data(
            Contract,
            bad_input,
            role="commercial"
        )
        assert res == {"error": "Invalid field: test"}

    def test_invalid_input_type_for_string_field(self):
        res = check_permission_and_data(
            Collaborator,
            {"name": 1234},
            role="gestion"
        )
        assert res == {"error": "Invalid value for field: name"}

    def test_invalid_input_type_for_integer_field(self):
        res = check_permission_and_data(
            Contract,
            {"total_cost": "1234"},
            role="gestion"
        )
        assert res == {"error": "Invalid value for field: total_cost"}

    def test_valid_email_input_field(self):
        res = check_permission_and_data(
            Collaborator,
            {"email": "test@test.com"},
            role="gestion"
        )
        assert res == {"email": "test@test.com"}

    def test_invalid_email_input_field(self):
        res = check_permission_and_data(
            Collaborator,
            {"email": "test.test.com"},
            role="gestion"
        )
        assert res == {"error": "Invalid value for field: email"}

    def test_valid_date_input_field(self):
        res = check_permission_and_data(
            Contract,
            {"date": "01/01/2011"},
            role="commercial"
        )
        assert res == {"date": "01/01/2011"}

    def test_invalid_date_input_field(self):
        res = check_permission_and_data(
            Contract,
            {"date": "1-1-2011"},
            role="commercial"
        )
        assert res == {"error": "Invalid value for field: date"}

    def test_valid_bool_input_field(self):
        res = check_permission_and_data(
            Contract,
            {"status": True},
            role="commercial"
        )
        assert res == {"status": True}

    def test_invalid_bool_input_field(self):
        res = check_permission_and_data(
            Contract,
            {"status": 1},
            role="commercial"
        )
        assert res == {"error": "Invalid value for field: status"}

    def test_valid_phone_input_field(self):
        res = check_permission_and_data(
            Collaborator,
            {"phone": "1234"},
            role="gestion"
        )
        assert res == {"phone": "1234"}

    def test_invalid_phone_input_field(self):
        res = check_permission_and_data(
            Collaborator,
            {"phone": "1234aaa"},
            role="gestion"
        )
        assert res == {"error": "Invalid value for field: phone"}

    def test_password_too_short(self):
        res = check_permission_and_data(
            Collaborator,
            {"password": "123"},
            role="gestion"
        )
        assert res == {"error": "Invalid value for field: password"}
