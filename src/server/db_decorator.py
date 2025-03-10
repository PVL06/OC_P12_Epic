from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse


def handle_db_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError:
            return JSONResponse({"error": "Integrity error"}, status_code=400)
        except Exception as e:
            print(e)
            return JSONResponse({"error": "Internal error"}, status_code=400)
    return wrapper
