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


def clean_data(class_name, data: dict, role: str) -> dict:
    valid_attrs = class_name.get_valid_attrs(role=role)
    for key in data.keys():
        if key not in valid_attrs:
            del data[key]
    return data
