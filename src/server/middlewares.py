import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt

from server.db_manager import DBManager

manager = DBManager()


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret = os.getenv("SECRET_KEY")

    async def dispatch(self, request: Request, call_next):
        if str(request.url).split("/")[-1] != "login":
            token = request.headers.get("Authorization")
            if token:
                try:
                    token = token.split(" ")[1]
                    payload = jwt.decode(token, self.secret, algorithms=["HS256"])
                    request.state.jwt_payload = payload
                except jwt.ExpiredSignatureError:
                    return JSONResponse({"error": "Token expired"}, status_code=401)
                except jwt.InvalidTokenError:
                    return JSONResponse({"error": "Invalid token"}, status_code=401)
                else:
                    response = await call_next(request)
                    return response
            else:
                return JSONResponse({"error": "No connected !"}, status_code=401)
        else:
            response = await call_next(request)
            return response


class DatabaseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, dispatch=None, testing=False):
        super().__init__(app, dispatch)
        self.testing = testing

    async def dispatch(self, request: Request, call_next):
        if self.testing:
            request.state.db = manager.get_test_session()
        else:
            request.state.db = manager.get_session()
        response = await call_next(request)
        return response
