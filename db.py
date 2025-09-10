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
    id: Mapped[int] = mapped_column(primary_key=True)
    callsign: Mapped[str] = mapped_column(unique=True)
    airframe: Mapped[str]
    flights: Mapped[List["Flight"]] = relationship(back_populates="callsign")

class Flight(db.Model):

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    start_time = Mapped[datetime]

    callsign_id = mapped_column(ForeignKey("callsign.id"))
    callsign = relationship(Callsign, back_populates="flights")

    tracks: Mapped[List["Track"]] = relationship(back_populates="flight")

class Track(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    flight_id = mapped_column(ForeignKey("flight.id"))
    flight = relationship("Flight", back_populates="tracks")

    position_latitude: Mapped[float]
    position_longitude: Mapped[float]
    position_altitude: Mapped[float]

    velocity_airpseed: Mapped[float]
    velocity_groundSpeed: Mapped[float]
    velocity_vertSpeed: Mapped[float]
    velocity_unitsSpeed: Mapped[str]

    timestamp = Mapped[datetime]

def get_callsigns():
    callsigns = db.session.execute(db.select(Callsign.callsign)).scalars().all()
    return callsigns

#Test Commit