import re

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


def check_permission_and_data(class_name, input_data: dict, role: str) -> dict | None:
    field_permissions = {
        "collaborator": {
            "gestion": ["name", "email", "phone", "password", "role_id"]
        },
        "client": {
            "commercial": ["name", "email", "phone", "company"]
        },
        "contract": {
            "gestion": ["client_id", "total_cost", "remaining_to_pay", "date", "status"],
            "commercial": ["total_cost", "remaining_to_pay", "date", "status"]
        },
        "event": {
            "gestion": ["support_id"],
            "commercial": ["contract_id", "event_start", "event_end", "location", "attendees", "note"],
            "support": ["event_start", "event_end", "location", "attendees", "note"]
        }
    }
    valid_fields = field_permissions[class_name.__tablename__].get(role)
    if valid_fields:
        valid_data = {}
        for field, value in input_data.items():
            if field in valid_fields:
                validated = validator(field, value)
                if validated:
                    valid_data[field] = value
                else:
                    return {"field_error": f"Invalid value for field: {field}"}
            else:
                return {"field_error": f"Invalid field: {field}"}
        if valid_data:
            return valid_data


def validator(field: str, value) -> bool:
    if field in ["name", "company", "location", "note"]:
        return isinstance(value, str)
    
    elif field[-3:] == "_id" or field in ["attendees", "total_cost", "remaining_to_pay"]:
        if isinstance(value, int):
            if value > 0:
                return True
        return False

    elif field == "email":
        if isinstance(value, str):
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            return re.match(pattern, value) is not None
        
    elif field == "phone":
        if isinstance(value, str):
            return value.isdigit()

    elif field == "password":
        if isinstance(value, str):
            return len(value) > 3
        
    elif field in ["date", "event_start", "event_end"]:
        pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
        return re.match(pattern, value)
    
    elif field == "status":
        return isinstance(value, bool)
    
    else:
        return False
