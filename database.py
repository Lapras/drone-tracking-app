from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from typing import List
import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Callsign(db.Model):
    __tablename__ = "callsigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    callsign: Mapped[str] = mapped_column(unique=True)
    airframe: Mapped[str]
    flights: Mapped[List["Flight"]] = relationship(back_populates="callsigns")

class Flight(db.Model):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    start_time = Mapped[datetime]

    callsign_id = mapped_column(ForeignKey("callsigns.id"))
    callsign = relationship(Callsign, back_populates="flights")

    tracks: Mapped[List["Track"]] = relationship(back_populates="flights")

    tracks: Mapped[["CumulativeDeviation"] = relationship(back_populates="flights"), uselist=False]

class Track(db.Model):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)

    flight_id = mapped_column(ForeignKey("flights.id"))
    flight = relationship("Flight", back_populates="tracks")

    position_id = mapped_column(ForeignKey("positions.id"))
    position: Mapped["Position"] = relationship(back_populates=("positions"), uselist=False)

    velocity_airpseed: Mapped[float]
    velocity_groundSpeed: Mapped[float]
    velocity_vertSpeed: Mapped[float]
    velocity_unitsSpeed: Mapped[str]

    timestamp = Mapped[datetime]

class Position(db.Model):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)

    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude: Mapped[float]

class ExpectedPosition(db.Model):
    __tablename__ = "expectedpositions"
    id: Mapped[int] = mapped_column(primary_key=True)

    position_id = mapped_column(ForeignKey("positions.id"))
    poisition: Mapped["Position"] = relationship(back_populates=("positions"), uselist=False)

    flight_id = mapped_column(ForeignKey("flightplans.id"))
    flight_plan = relationship("FlightPlan", back_populates="expectedpositions")

    order: Mapped[int]

class FlightPlan(db.Model):
    __tablename__ = "flightplans"

    id: Mapped[int] = mapped_column(primary_key=True)

    expected_positions: Mapped[List["ExpectedPosition"]] = relationship(back_populates="flightplans")


def get_callsigns():
    callsigns = db.session.execute(db.select(Callsign.callsign)).scalars().all()
    return callsigns

class CumulativeDeviation(db.Model):
    __tablename__ = "cumulativedeviations"

    id: Mapped[int] = mapped_column(primary_key=True)

    flight_id = mapped_column(ForeignKey("callsigns.id"))
    flight = relationship(Callsign, back_populates="flights")