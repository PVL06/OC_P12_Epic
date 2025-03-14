from sqlalchemy import select
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request

from server.db_manager import DBManager
from server.models import Client, Contract, Event
from server.utils import handle_db_errors, check_permission_and_data


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
        with request.state.db.begin() as session:
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
        data = await request.json()
        cleaned_data = check_permission_and_data(Client, data, user.get("role"))
        if cleaned_data:

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            cleaned_data["commercial_id"] = user.get("id")
            new_client = Client(**cleaned_data)
            with request.state.db.begin() as session:
                session.add(new_client)
                return JSONResponse({"status": "Client created"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_client(request: Request):
        user = request.state.jwt_payload
        data = await request.json()
        cleaned_data = check_permission_and_data(Client, data, user.get("role"))
        if cleaned_data:

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            stmt = select(Client).where(Client.id == request.path_params["id"])
            with request.state.db.begin() as session:
                client = session.scalar(stmt)
                if client.commercial_id == user.get("id"):
                    for field, value in cleaned_data.items():
                        setattr(client, field, value)
                    return JSONResponse({"status": "Client updated"})
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
        with request.state.db.begin() as session:
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
            cleaned_data = check_permission_and_data(Contract, data, user_role)

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            stmt = select(Client).where(Client.id == cleaned_data.get("client_id"))
            with request.state.db.begin() as session:
                client = session.scalar(stmt)
                if client:
                    cleaned_data["commercial_id"] = client.commercial_id
                    new_contract = Contract(**cleaned_data)
                    session.add(new_contract)
                    return JSONResponse({"status": "contract created"})
                else:
                    return JSONResponse({"error": "Invalid client"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_contract(request: Request) -> JSONResponse:
        user = request.state.jwt_payload
        data = await request.json()
        cleaned_data = check_permission_and_data(Contract, data, user.get("role"))
        if cleaned_data:

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            stmt = select(Contract).where(Contract.id == request.path_params["id"])
            with request.state.db.begin() as session:
                contract = session.scalar(stmt)
                if contract:
                    if user.get("role") == "commercial" and contract.commercial_id != user.get("id"):
                        return JSONResponse({"error": "Not your client"})
                    for field, value in cleaned_data.items():
                        setattr(contract, field, value)
                    return JSONResponse({"status": "Contract updated"})
                else:
                    return JSONResponse({"error": "Invalid contract"})
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
        with request.state.db.begin() as session:
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
            cleaned_data = check_permission_and_data(Event, data, role=user.get("role"))

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            stmt = select(Contract).where(Contract.id == data.get("contract_id"))
            with request.state.db.begin() as session:
                contract = session.scalar(stmt)
                if contract:
                    if contract.commercial_id == user.get("id"):
                        cleaned_data["client_id"] = contract.client_id
                        event = Event(**cleaned_data)
                        session.add(event)
                        return JSONResponse({"status": "Event created"})
                    else:
                        return JSONResponse({"error": "Not your client"})
                else:
                    return JSONResponse({"error": "Invalid contract id"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_event(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")

        if user_role in ["gestion", "support"]:
            data = await request.json()
            cleaned_data = check_permission_and_data(Event, data, role=user_role)

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            stmt = select(Event).where(Event.id == request.path_params["id"])
            with request.state.db.begin() as session:
                event = session.scalar(stmt)
                if event:
                    for field, value in cleaned_data.items():
                        setattr(event, field, value)
                    return JSONResponse({"status": "Event updated"})
                else:
                    return JSONResponse({"error": "Invalid event id"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
