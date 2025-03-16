import os
import datetime

from sqlalchemy import select
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request
import argon2
import jwt

from server.db_manager import DBManager
from server.models import Collaborator
from server.permissions import handle_db_errors, check_permission_and_data

manager = DBManager()


class CollabAPI:

    @classmethod
    def get_routes(cls) -> list[Route]:
        return [
            Route('/login', cls.login, methods=["POST"]),
            Route('/session', cls.session, methods=["GET"]),
            Route('/collab', cls.get_collaborators, methods=["GET"]),
            Route('/collab/create', cls.create_collaborator, methods=["POST"]),
            Route('/collab/update/{id}', cls.update_collaborator, methods=["POST"]),
            Route('/collab/delete/{id}', cls.delete_collaborator, methods=["GET"])
        ]

    @staticmethod
    @handle_db_errors
    async def login(request: Request) -> JSONResponse:
        data = await request.json()
        stmt = select(Collaborator).where(Collaborator.email == data.get("email"))
        with request.state.db.begin() as session:
            collab = session.scalar(stmt)
            if collab:
                # check password
                try:
                    ph = argon2.PasswordHasher()
                    ph.verify(collab.password, data.get("password"))
                except argon2.exceptions.VerificationError:
                    return JSONResponse({"error": "Invalid password !"})
                else:
                    # create jwt token
                    token = jwt.encode(
                        {
                            "id": collab.id,
                            "name": collab.name,
                            "role": collab.role.__str__(),
                            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
                        },
                        os.getenv("SECRET_KEY"),
                        algorithm="HS256"
                    )
                    return JSONResponse(
                        {
                            "status": "Connected",
                            "jwt_token": "Bearer " + token
                        }
                    )
            return JSONResponse({"error": "email invalid !"})

    @staticmethod
    @handle_db_errors
    async def session(request: Request) -> JSONResponse:
        payload = request.state.jwt_payload
        return JSONResponse(
            {
                "id": payload.get("id"),
                "role": payload.get("role")
            }
        )

    @staticmethod
    @handle_db_errors
    async def get_collaborators(request: Request) -> JSONResponse:
        stmt = select(Collaborator)
        with request.state.db.begin() as session:
            data = session.scalars(stmt).all()
            collaborators = []
            for collab in data:
                collaborators.append(
                    {
                        "id": collab.id,
                        "complet_name": collab.name,
                        "email": collab.email,
                        "phone": collab.phone,
                        "role_id": collab.role.__str__()
                    }
                )
        return JSONResponse({'collaborators': collaborators})

    @staticmethod
    @handle_db_errors
    async def create_collaborator(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")
        data = await request.json()
        cleaned_data = check_permission_and_data(Collaborator, data, user_role)
        if cleaned_data:

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            ph = argon2.PasswordHasher()
            cleaned_data["password"] = ph.hash(cleaned_data["password"])
            new_collab = Collaborator(**cleaned_data)

            with request.state.db.begin() as session:
                session.add(new_collab)
                return JSONResponse({"status": "New collaborator created"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_collaborator(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")
        data = await request.json()
        cleaned_data = check_permission_and_data(Collaborator, data, user_role)
        if cleaned_data:

            if cleaned_data.get("error"):
                return JSONResponse(cleaned_data)

            stmt = select(Collaborator).where(Collaborator.id == request.path_params["id"])
            with request.state.db.begin() as session:
                collab = session.scalar(stmt)
                if collab:
                    for field, value in cleaned_data.items():
                        setattr(collab, field, value)
                    return JSONResponse({"status": "Collaborator updated"})
                return JSONResponse({"error": "Invalid collaborator id"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def delete_collaborator(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")
        if user_role == "gestion":
            stmt = select(Collaborator).where(Collaborator.id == request.path_params["id"])
            with request.state.db.begin() as session:
                collab = session.scalar(stmt)
                if collab:
                    session.delete(collab)
                    return JSONResponse({"status": "Collaborator deleted"})
                return JSONResponse({"error": "Invalid collaborator id"})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
