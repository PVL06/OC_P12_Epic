import datetime

from sqlalchemy import ForeignKey, String, DateTime, Date, Integer, Text, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Collaborator(Base):
    __tablename__ = "collaborator"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complet_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(255))

    def __str__(self):
        return f"Collaborator: {self.complet_name}"


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20), unique=True)


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    company: Mapped[str] = mapped_column(String(255))
    create_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    commercial_id: Mapped[int] = mapped_column(ForeignKey("collaborator.id"))

    def __str__(self):
        return f"Client: {self.client_name}"


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    commercial_id: Mapped[int] = mapped_column(ForeignKey("collaborator.id"))
    total_cost: Mapped[float] = mapped_column(Float)
    remaining_to_pay: Mapped[float] = mapped_column(Float)
    date: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[bool] = mapped_column(Boolean)

    def __str__(self):
        return f"Contract {self.id}"


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    event_start: Mapped[datetime.date] = mapped_column(Date)
    event_end: Mapped[datetime.date] = mapped_column(Date)
    support_id: Mapped[int] = mapped_column(ForeignKey("collaborator.id"))
    location: Mapped[str] = mapped_column(String(255))
    attendees: Mapped[int] = mapped_column(Integer)
    note: Mapped[str] = mapped_column(Text)

    def __str__(self):
        return f"Event {self.id}"
