import datetime

from sqlalchemy import ForeignKey, String, DateTime, Date, Integer, Text, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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

    clients: Mapped[list["Client"]] = relationship(back_populates="commercial")
    contracts: Mapped["Contract"] = relationship(back_populates="commercial")
    supports: Mapped["Event"] = relationship(back_populates="support")

    def __str__(self):
        return self.complet_name

    def to_dict(self):
        return {
            "id": self.id,
            "complet_name": self.complet_name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password
        }


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

    commercial: Mapped["Collaborator"] = relationship(back_populates="clients")
    contracts: Mapped["Contract"] = relationship(back_populates="client")
    events: Mapped["Event"] = relationship(back_populates="client")

    def __str__(self):
        return self.client_name

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "create_data": self.create_date,
            "update_date": self.update_date,
            "commercial": self.commercial.__str__()
        }


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

    def __str__(self):
        return self.id

    def to_dict(self):
        return {
            "id": self.id,
            "client": self.client.__str__(),
            "commercial": self.commercial.__str__(),
            "total_cost": self.total_cost,
            "remaining_to_pay": self.remaining_to_pay,
            "date": self.date,
            "status": self.status
        }


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

    def __str__(self):
        return self.id

    def to_string(self):
        return {
            "id": self.id,
            "contract": self.contract_id,
            "client": self.client.__str__(),
            "event_start": self.event_start,
            "event_end": self.event_end,
            "support": self.support.__str__()
        }
