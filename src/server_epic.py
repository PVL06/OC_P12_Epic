import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware

from server.api_collab import CollabAPI
from server.api_work import ClientAPI, ContractAPI, EventAPI
from server.middlewares import JWTMiddleware


api_routes = [
    CollabAPI.get_routes(),
    ClientAPI.get_routes(),
    ContractAPI.get_routes(),
    EventAPI.get_routes()
]


all_routes = []
for routes in api_routes:
    all_routes.extend(routes)

middlewares = [
    Middleware(JWTMiddleware)
]

app = Starlette(
    debug=True,
    routes=all_routes,
    middleware=middlewares
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
