from sqlalchemy import select, false, true
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request

from sentry_sdk import capture_message
from server.models import Collaborator, Client, Contract, Event
from server.permissions import handle_db_errors, check_permission_and_data


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
        if commercial_id := request.query_params.get("commercial_id"):
            stmt = stmt.join(Collaborator).filter(Collaborator.id == commercial_id)
        elif "unassigned" in request.query_params:
            stmt = stmt.filter(Client.commercial_id.is_(None))
        with request.state.db.begin() as session:
            data = session.scalars(stmt).all()
            clients = [
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
                for client in data
            ]
        return JSONResponse({"clients": clients})

    @staticmethod
    @handle_db_errors
    async def create_client(request: Request) -> JSONResponse:
        role = request.state.jwt_payload.get("role")
        user_id = request.state.jwt_payload.get("id")
        if role == "commercial":
            data = await request.json()
            cleaned_data = check_permission_and_data(Client, data, role)
            if cleaned_data:

                if cleaned_data.get("error"):
                    return JSONResponse(cleaned_data, status_code=400)

                cleaned_data["commercial_id"] = user_id
                new_client = Client(**cleaned_data)
                with request.state.db.begin() as session:
                    session.add(new_client)
                    return JSONResponse({"status": "Client created"})

        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_client(request: Request):
        role = request.state.jwt_payload.get("role")
        user_id = request.state.jwt_payload.get("id")
        data = await request.json()
        cleaned_data = check_permission_and_data(Client, data, role)
        if cleaned_data:

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data, status_code=400)

            stmt = select(Client).where(Client.id == request.path_params["id"])
            with request.state.db.begin() as session:
                client = session.scalar(stmt)
                commecial_condition = all([role == "commercial", client.commercial_id == user_id])
                support_condition = all([role == "gestion" and client.commercial_id is None])
                if commecial_condition or support_condition:
                    for field, value in cleaned_data.items():
                        setattr(client, field, value)
                    return JSONResponse({"status": "Client updated"})
                else:
                    capture_message("Outside the CLI application", "warning")
                    return JSONResponse(
                        {"error": "Not your client" if commecial_condition else "Commercial already assigned"},
                        status_code=400
                    )
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
        if request.query_params.get("commercial_id"):
            stmt = stmt.join(Collaborator)
        for key, value in request.query_params.items():
            match key:
                case "commercial_id":
                    stmt = stmt.filter(
                        Collaborator.id == int(value),
                        Contract.status == true()
                    )
                case "no_signed":
                    stmt = stmt.filter(Contract.status == false())
                case "debtor":
                    stmt = stmt.filter(Contract.remaining_to_pay > 0)

        with request.state.db.begin() as session:
            data = session.scalars(stmt).all()
            contracts = [
                {
                    "id": contract.id,
                    "client": contract.client.__str__(),
                    "commercial": contract.commercial.__str__(),
                    "event_title": contract.event_title,
                    "total_cost": contract.total_cost,
                    "remaining_to_pay": contract.remaining_to_pay,
                    "date": contract.date.strftime("%d/%m/%Y"),
                    "status": contract.status
                }
                for contract in data
            ]
        return JSONResponse({"contracts": contracts})

    @staticmethod
    @handle_db_errors
    async def create_contract(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")
        if user_role == "gestion":
            data = await request.json()
            cleaned_data = check_permission_and_data(Contract, data, user_role)

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data, status_code=400)

            stmt = select(Client).where(Client.id == cleaned_data.get("client_id"))
            with request.state.db.begin() as session:
                client = session.scalar(stmt)
                if client:
                    cleaned_data["commercial_id"] = client.commercial_id
                    new_contract = Contract(**cleaned_data)
                    session.add(new_contract)
                    return JSONResponse({"status": "contract created"})
                else:
                    capture_message("Outside the CLI application", "warning")
                    return JSONResponse({"error": "Invalid client"}, status_code=400)
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
                return JSONResponse(cleaned_data, status_code=400)

            stmt = select(Contract).where(Contract.id == request.path_params["id"])
            with request.state.db.begin() as session:
                contract = session.scalar(stmt)
                if contract:
                    if user.get("role") == "commercial" and contract.commercial_id != user.get("id"):
                        return JSONResponse({"error": "Not your client"}, status_code=400)
                    for field, value in cleaned_data.items():
                        setattr(contract, field, value)
                    return JSONResponse({"status": "Contract updated"})
                else:
                    capture_message("Outside the CLI application", "warning")
                    return JSONResponse({"error": "Invalid contract"}, status_code=400)
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
        if support_id := request.query_params.get("support_id"):
            stmt = stmt.join(Collaborator).filter(Collaborator.id == support_id)
        elif "no_support" in request.query_params.keys():
            stmt = stmt.filter(Event.support_id.is_(None))

        with request.state.db.begin() as session:
            data = session.scalars(stmt).all()
            events = [
                {
                    "id": event.id,
                    "contract": event.contract_id.__str__(),
                    "client": event.client.__str__(),
                    "title": event.contract.event_title,
                    "event_start": event.event_start.strftime("%d/%m/%Y %H:%M"),
                    "event_end": event.event_end.strftime("%d/%m/%Y %H:%M"),
                    "support": event.support.__str__(),
                    "location": event.location,
                    "attendees": event.attendees,
                    "note": event.note
                }
                for event in data
            ]
        return JSONResponse({"events": events})

    @staticmethod
    @handle_db_errors
    async def create_event(request: Request) -> JSONResponse:
        user = request.state.jwt_payload

        if user.get("role") == "commercial":
            data = await request.json()
            cleaned_data = check_permission_and_data(Event, data, role=user.get("role"))

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data, status_code=400)

            stmt = select(Contract).where(Contract.id == data.get("contract_id"))
            with request.state.db.begin() as session:
                contract = session.scalar(stmt)
                if contract:
                    stmt = select(Event).where(Event.contract_id == contract.id)
                    event = session.scalar(stmt)
                    if event is None:
                        conditions = [
                            contract.commercial_id == user.get("id"),
                            contract.status
                        ]
                        if all(conditions):
                            cleaned_data["client_id"] = contract.client_id
                            event = Event(**cleaned_data)
                            session.add(event)
                            return JSONResponse({"status": "Event created"})
                        else:
                            capture_message("Outside the CLI application", "warning")
                            return JSONResponse({"error": "Not your client or contract unsigned"}, status_code=400)
                    else:
                        return JSONResponse({"error": "Event is already created for this contract"}, status_code=400)
                else:
                    capture_message("Outside the CLI application", "warning")
                    return JSONResponse({"error": "Invalid contract id"}, status_code=400)
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_event(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")
        user_id = request.state.jwt_payload.get("id")

        if user_role in ["gestion", "support"]:
            data = await request.json()
            cleaned_data = check_permission_and_data(Event, data, role=user_role)

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data, status_code=400)

            stmt = select(Event).where(Event.id == request.path_params["id"])
            with request.state.db.begin() as session:
                event = session.scalar(stmt)
                if event:
                    if user_role == "support" and event.support_id != user_id:
                        capture_message("Outside the CLI application", "warning")
                        return JSONResponse({"error": "Not your event"}, status_code=400)
                    for field, value in cleaned_data.items():
                        setattr(event, field, value)
                    return JSONResponse({"status": "Event updated"})
                else:
                    capture_message("Outside the CLI application", "warning")
                    return JSONResponse({"error": "Invalid event id"}, status_code=400)
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
