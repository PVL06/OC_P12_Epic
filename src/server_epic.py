import uvicorn
from starlette.applications import Starlette
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from server.config import SENTRY_DSN
from server.api_collab import CollabAPI
from server.api_work import ClientAPI, ContractAPI, EventAPI
from server.middlewares import JWTMiddleware, DatabaseMiddleware

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,
    send_default_pii=True
)

api_routes = [
    CollabAPI.get_routes(),
    ClientAPI.get_routes(),
    ContractAPI.get_routes(),
    EventAPI.get_routes()
]


all_routes = []
for routes in api_routes:
    all_routes.extend(routes)

app = Starlette(
    debug=True,
    routes=all_routes
)

app.add_middleware(JWTMiddleware)
app.add_middleware(DatabaseMiddleware)
app.add_middleware(SentryAsgiMiddleware)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
