from sqlalchemy import select, inspect
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request

from server.db_manager import DBManager
from server.models import Client, Contract, Event
from server.db_decorator import handle_db_errors, clean_data


manager = DBManager()


class ClientAPI:
    @classmethod
    def get_routes(cls):
        return [
            Route('/client', cls.get_clients, methods=["GET"]),
            Route('/client/create', cls.create_client, methods=["POST"]),
            Route('/client/update/{id}', cls.update_client, methods=["POST"])
        ]

    @staticmethod
    @handle_db_errors
    async def get_clients(request: Request) -> JSONResponse:
        stmt = select(Client)

        new_session = manager.get_session()
        with new_session.begin() as session:
            data = session.scalars(stmt).all()
            clients = []
            for client in data:
                clients.append(
                    {
                        "id": client.id,
                        "name": client.name,
                        "email": client.email,
                        "phone": client.phone,
                        "company": client.company,
                        "create_date": client.create_date.strftime("%d-%m-%Y %H:%M:%S"),
                        "update_date": client.update_date.strftime(
                            "%d-%m-%Y %H:%M:%S"
                        ) if client.update_date else "never updated",
                        "commercial": client.commercial.__str__()
                    }
                )
        return JSONResponse({"clients": clients})

    @staticmethod
    @handle_db_errors
    async def create_client(request: Request) -> JSONResponse:
        user = request.state.jwt_payload

        if user.get("role") == "commercial":
            data = await request.json()
            data["commercial_id"] = user.get("id")
            new_client = Client(**data)
            new_session = manager.get_session()
            with new_session.begin() as session:
                session.add(new_client)
                return JSONResponse({"status": True})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_client(request: Request):
        user = request.state.jwt_payload

        if user.get("role") == "commercial":
            data = await request.json()
            attrs = inspect(Client).attrs.keys()
            stmt = select(Client).where(Client.id == request.path_params["id"])

            new_session = manager.get_session()
            with new_session.begin() as session:
                client = session.scalar(stmt)
                if client.commercial_id == user.get("id"):
                    for field, value in data.items():
                        if field in attrs:
                            setattr(client, field, value)
                    return JSONResponse({"status": True})
                else:
                    return JSONResponse({"error": "Not your client"}, status_code=401)
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)


class ContractAPI:
    @classmethod
    def get_routes(cls) -> list[Route]:
        return [
            Route('/contract', cls.get_contracts, methods=["GET"]),
            Route('/contract/create', cls.create_contract, methods=["POST"]),
            Route('/contract/update/{id}', cls.update_contract, methods=["POST"])
        ]

    @staticmethod
    @handle_db_errors
    async def get_contracts(request: Request) -> JSONResponse:
        stmt = select(Contract)

        new_session = manager.get_session()
        with new_session.begin() as session:
            data = session.scalars(stmt).all()
            contracts = []
            for contract in data:
                contracts.append(
                    {
                        "id": contract.id,
                        "client": contract.client.__str__(),
                        "commercial": contract.commercial.__str__(),
                        "total_cost": contract.total_cost,
                        "remaining_to_pay": contract.remaining_to_pay,
                        "date": contract.date.strftime("%d-%m-%Y"),
                        "status": contract.status
                    }
                )
        return JSONResponse({"contracts": contracts})

    @staticmethod
    @handle_db_errors
    async def create_contract(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")

        if user_role == "gestion":
            data = await request.json()

            # clean data
            attrs = Contract.get_attrs()
            for key in data.keys():
                if key not in attrs:
                    del data[key]

            stmt = select(Client).where(Client.id == data.get("client_id"))

            new_session = manager.get_session()
            with new_session.begin() as session:
                client = session.scalar(stmt)
                data["commercial_id"] = client.commercial_id
                new_contract = Contract(**data)
                session.add(new_contract)
                return JSONResponse({"status": True})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_contract(request: Request) -> JSONResponse:
        user = request.state.jwt_payload

        if user.get("role") in ["gestion", "commercial"]:
            data = await request.json()
            attrs = inspect(Contract).attrs.keys()
            stmt = select(Contract).where(Contract.id == request.path_params["id"])

            new_session = manager.get_session()
            with new_session.begin() as session:
                contract = session.scalar(stmt)
                if user.get("role") == "commercial" and contract.commercial_id != user.get("id"):
                    return JSONResponse({"error": "Not your client"})
                for field, value in data.items():
                    if field in attrs:
                        setattr(contract, field, value)
            return JSONResponse({"status": True})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)


class EventAPI:
    @classmethod
    def get_routes(cls) -> list[Route]:
        return [
            Route('/event', cls.get_events, methods=["GET"]),
            Route('/event/create', cls.create_event, methods=["POST"]),
            Route('/event/update/{id}', cls.update_event, methods=["POST"])
        ]

    @staticmethod
    @handle_db_errors
    async def get_events(request: Request) -> JSONResponse:
        stmt = select(Event)

        new_session = manager.get_session()
        with new_session.begin() as session:
            data = session.scalars(stmt).all()
            events = []
            for event in data:
                events.append(
                    {
                        "id": event.id,
                        "contract": event.contract_id.__str__(),
                        "client": event.client.__str__(),
                        "event_start": event.event_start.strftime("%d-%m-%Y"),
                        "event_end": event.event_end.strftime("%d-%m-%Y"),
                        "support": event.support.__str__(),
                        "location": event.location,
                        "attendees": event.attendees,
                        "note": event.note
                    }
                )
        return JSONResponse({"events": events})

    @staticmethod
    @handle_db_errors
    async def create_event(request: Request) -> JSONResponse:
        user = request.state.jwt_payload

        if user.get("role") == "commercial":
            data = await request.json()
            cleaned_data = clean_data(Event, data, role=user.get("role"))

            stmt = select(Contract).where(Contract.id == data.get("contract_id"))

            new_session = manager.get_session()
            with new_session.begin() as session:

                contract = session.scalar(stmt)
                if contract.commercial_id == user.get("id"):
                    data["client_id"] = contract.client_id
                    event = Event(**cleaned_data)
                    session.add(event)
                    return JSONResponse({"status": True})
                else:
                    return JSONResponse({"error": "Not your client"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_event(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")

        if user_role in ["gestion", "support"]:
            data = await request.json()
            cleaned_data = clean_data(Event, data, role=user_role)
            stmt = select(Event).where(Event.id == request.path_params["id"])

            new_session = manager.get_session()
            with new_session.begin() as session:
                event = session.scalar(stmt)
                for field, value in cleaned_data.items():
                    setattr(event, field, value)
            return JSONResponse({"status": True})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
