from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from typing import List
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Callsign(db.Model):
    __tablename__ = "callsigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    callsign: Mapped[str] = mapped_column(unique=True)
    airframe: Mapped[str]
    flights: Mapped[List["Flight"]] = relationship(back_populates="callsign")

    def __init__(self, callsign : str, airframe : str):
        self.callsign = callsign
        self.airframe = airframe
        self.flights = [Flight(name="currentflight")]

    def get_current_flight(self):
        return next((f for f in self.flights if f.name == "currentflight"), None)


class CumulativeDeviation(db.Model):
    __tablename__ = "cumulativedeviations"

    id: Mapped[int] = mapped_column(primary_key=True, default=0.0)

    flight_id = mapped_column(ForeignKey("flights.id"))

class Flight(db.Model):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    # start_time = Mapped[datetime]

    callsign_id = mapped_column(ForeignKey("callsigns.id"))
    callsign = relationship(Callsign, back_populates="flights")

    tracks: Mapped[List["Track"]] = relationship(back_populates="flight")

    deviation: Mapped["CumulativeDeviation"] = relationship("CumulativeDeviation", uselist=False)

class Track(db.Model):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)

    flight_id = mapped_column(ForeignKey("flights.id"))
    flight = relationship("Flight", back_populates="tracks")

    position_id = mapped_column(ForeignKey("positions.id"))
    position: Mapped["Position"] = relationship("Position", uselist=False)

    velocity_airpseed: Mapped[float]
    velocity_groundSpeed: Mapped[float]
    velocity_vertSpeed: Mapped[float]
    velocity_unitsSpeed: Mapped[str]

    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

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
    poisition: Mapped["Position"] = relationship("Position", uselist=False)

    flight_id = mapped_column(ForeignKey("flightplans.id"))

    order: Mapped[int]

class FlightPlan(db.Model):
    __tablename__ = "flightplans"

    id: Mapped[int] = mapped_column(primary_key=True)

    expected_positions: Mapped[List["ExpectedPosition"]] = relationship("ExpectedPosition")

def create_all():
    db.create_all()

def get_callsigns():
    result = db.session.execute(text("SELECT callsign FROM callsigns")).fetchall()
    print(result)
    callsigns = db.session.execute(db.select(Callsign.callsign)).scalars().all()
    return callsigns

def get_callsign_flight(callsign_str):
    callsign = db.session.query(Callsign).filter_by(callsign=callsign_str).first()
    if callsign:
        return callsign.get_current_flight()

def get_cum_deviation_for_callsign(callsign_str):
    callsign = db.session.query(Callsign).filter_by(callsign=callsign_str).first()
    if callsign:
        return callsign.get_current_flight()
def add_track(flight, position):
    db.session.add(position)

    track = Track(
        flight_id=flight.id,
        position_id = position.id
    )

    db.session.add(track)
    db.session.commit()


def commit_session():
    db.session.commit()

def cycle_flights():
    callsigns = db.session.query(Callsign).all()

    for callsign in callsigns:
        current = callsign.get_current_flight()
        
        if current:
            existing_flights = len(callsign.flights)
            current.name = f"flight{existing_flights}"

        new_flight = Flight(name="currentflight")
        callsign.flights.append(new_flight)
    
    db.session.commit()