import os
import datetime

from sqlalchemy import select, inspect
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request
import argon2
import jwt

from server.db_manager import DBManager
from server.models import Collaborator
from server.db_decorator import handle_db_errors

manager = DBManager()


class CollabAPI:

    @classmethod
    def get_routes(cls):
        return [
            Route('/login', cls.login, methods=["POST"]),
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

        new_session = manager.get_session()
        with new_session.begin() as session:
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
                    return JSONResponse({"jwt_token": token})
            return JSONResponse({"error": "email invalid !"})

    @staticmethod
    @handle_db_errors
    async def get_collaborators(request: Request) -> JSONResponse:
        stmt = select(Collaborator)
        new_session = manager.get_session()
        with new_session.begin() as session:
            data = session.scalars(stmt).all()
            return_data = []
            for collab in data:
                return_data.append(
                    {
                        "id": collab.id,
                        "complet_name": collab.name,
                        "email": collab.email,
                        "phone": collab.phone,
                        "role_id": collab.role.__str__()
                    }
                )
        return JSONResponse({'collaborators': return_data})

    @staticmethod
    @handle_db_errors
    async def create_collaborator(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")

        if user_role == "gestion":
            data = await request.json()
            ph = argon2.PasswordHasher()
            new_collab = Collaborator(
                name=data.get("name"),
                email=data.get("email"),
                phone=data.get("phone"),
                password=ph.hash(data.get("password")),
                role_id=data.get("role_id")
            )
            new_session = manager.get_session()
            with new_session.begin() as session:
                session.add(new_collab)
                return JSONResponse({'status': True})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def update_collaborator(request: Request):
        user_role = request.state.jwt_payload.get("role")
        if user_role == "gestion":
            data = await request.json()
            stmt = select(Collaborator).where(Collaborator.id == request.path_params["id"])
            attrs = inspect(Collaborator).attrs.keys()

            new_session = manager.get_session()
            with new_session.begin() as session:
                collab = session.scalar(stmt)
                if collab:
                    for field, value in data.items():
                        if field in attrs:
                            setattr(collab, field, value)
                    return JSONResponse({"status": True})
                return JSONResponse({"status": False})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

    @staticmethod
    @handle_db_errors
    async def delete_collaborator(request: Request) -> JSONResponse:
        user_role = request.state.jwt_payload.get("role")
        if user_role == "gestion":
            stmt = select(Collaborator).where(Collaborator.id == request.path_params["id"])

            new_session = manager.get_session()
            with new_session.begin() as session:
                collab = session.scalar(stmt)
                if collab:
                    session.delete(collab)
                    return JSONResponse({"status": True})
                return JSONResponse({"statut": False})
        else:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
