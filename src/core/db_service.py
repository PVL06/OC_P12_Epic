from sqlalchemy import select, inspect

from core.db_manager import DBManager


class DBService:
    def __init__(self):
        self.session = DBManager().get_session()

    def create(self, model_class, data: dict) -> None:
        obj = model_class(**data)

        with self.session.begin() as session:
            session.add(obj)

    def get_all(self, model_class) -> list[dict]:
        stmt = select(model_class)

        with self.session.begin() as session:
            response = session.scalars(stmt).all()
            data = [obj.to_dict() for obj in response]

        return data

    def get_one(self, model_class, id: int) -> dict:
        stmt = select(model_class)
        stmt.where(model_class.id == id)

        with self.session.begin() as session:
            response = session.scalar(stmt)
            data = response.to_dict()

        return data

    def update(self, model_class, id: int, data: dict) -> None:
        stmt = select(model_class)
        stmt.where(model_class.id == id)
        attrs = inspect(model_class).attrs.keys()

        with self.session.begin() as session:
            obj = session.scalar(stmt)
            for key, value in data.items():
                if key in attrs:
                    setattr(obj, key, value)

    def delete(self, model_class, id: int) -> None:
        with self.session.begin() as session:
            stmt = select(model_class)
            stmt.where(model_class.id == id)
            obj = session.scalar(stmt)
            session.delete(obj)
