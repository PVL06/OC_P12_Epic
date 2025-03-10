import datetime

from sqlalchemy import ForeignKey, String, DateTime, Date, Integer, Text, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Collaborator(Base):
    __tablename__ = "collaborator"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))

    role: Mapped["Role"] = relationship(back_populates="roles")
    clients: Mapped[list["Client"]] = relationship(back_populates="commercial")
    contracts: Mapped["Contract"] = relationship(back_populates="commercial")
    supports: Mapped["Event"] = relationship(back_populates="support")

    def __str__(self):
        return self.name


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20), unique=True)

    roles: Mapped["Collaborator"] = relationship(back_populates="role")

    def __str__(self):
        return self.role


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    company: Mapped[str] = mapped_column(String(255))
    create_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    commercial_id: Mapped[int] = mapped_column(ForeignKey("collaborator.id"))

    commercial: Mapped["Collaborator"] = relationship(back_populates="clients")
    contracts: Mapped["Contract"] = relationship(back_populates="client")
    events: Mapped["Event"] = relationship(back_populates="client")

    def __str__(self):
        return self.name
    
    @classmethod
    def get_valid_attrs(cls, role="") -> list[str]:
        return [
            "name",
            "email",
            "phone",
            "company"
        ]
    # voir si commercial supprimer de reattribuer le client a un autre commercial


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    commercial_id: Mapped[int] = mapped_column(ForeignKey("collaborator.id"))
    total_cost: Mapped[float] = mapped_column(Float)
    remaining_to_pay: Mapped[float] = mapped_column(Float)
    date: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[bool] = mapped_column(Boolean)

    client: Mapped["Client"] = relationship(back_populates="contracts")
    commercial: Mapped["Collaborator"] = relationship(back_populates="contracts")
    event: Mapped["Event"] = relationship(back_populates="contract")

    def __str__(self):
        return self.id

    @classmethod
    def get_valid_attrs(cls, role: str) -> list[str]:
        if role == "support":
            return [
                "client_id",
                "commercial_id",
                "total_cost",
                "remaining_to_pay",
                "date",
                "status"
            ]
        elif role == "commercial":
            return [
                "total_cost",
                "remaining_to_pay",
                "date",
                "status"
            ]
        


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

    client: Mapped["Client"] = relationship(back_populates="events")
    support: Mapped["Collaborator"] = relationship(back_populates="supports")
    contract: Mapped["Contract"] = relationship(back_populates="event")

    __table_args__ = (UniqueConstraint("contract_id"),)

    def __str__(self):
        return self.id

    @classmethod
    def get_valid_attrs(cls, role: str) -> list[str]:
        if role == "gestion":
            return [
                "support_id"
            ]
        elif role == "support":
            return [
                "event_start",
                "event_end",
                "location",
                "attendees",
                "note"
            ]
        elif role == "commercial":
            return [
                "contract_id",
                "event_start",
                "event_end",
                "location",
                "attendees",
                "note"
            ]
