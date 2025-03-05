from sqlalchemy import select, inspect


class DBService:
    def __init__(self, session):
        self.session = session

    def create(self, model_class, data: dict) -> bool:
        obj = model_class(**data)

        with self.session.begin() as session:
            session.add(obj)
            return True
        return False

    def get_all(self, model_class) -> list[dict] | None:
        stmt = select(model_class)

        with self.session.begin() as session:
            response = session.scalars(stmt).all()
            if response:
                return [obj.to_dict() for obj in response]

    def get_one(self, model_class, id: int) -> dict | None:
        stmt = select(model_class).where(model_class.id == id)

        with self.session.begin() as session:
            response = session.scalar(stmt)
            if response:
                return response.to_dict()

    def update(self, model_class, id: int, data: dict) -> bool:
        stmt = select(model_class).where(model_class.id == id)
        attrs = inspect(model_class).attrs.keys()

        with self.session.begin() as session:
            obj = session.scalar(stmt)
            if obj:
                for key, value in data.items():
                    if key in attrs:
                        setattr(obj, key, value)
                return True
        return False

    def delete(self, model_class, id: int) -> bool:
        with self.session.begin() as session:
            stmt = select(model_class).where(model_class.id == id)
            obj = session.scalar(stmt)
            if obj:
                session.delete(obj)
                return True
        return False
