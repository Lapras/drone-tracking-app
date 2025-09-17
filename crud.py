# crud.py
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from database import Callsign, Flight, Deviation, Track, Position, Velocity
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy 

# Callsign helper
def create_callsign_with_current_flight(callsign: str, airframe: str | None = None) -> Callsign:
    cs = Callsign(callsign=callsign, airframe=airframe)
    db.session.add(cs)
    db.session.flush()  # assign cs.id

    current = Flight(name="currentflight", is_current=True, callsign=cs)
    current.deviation = Deviation(cumulative=0.0, recent=0.0)

    db.session.add(current)
    db.session.commit()
    return cs

def get_callsigns() -> list[str]:
    # ORM-only (no raw SQL needed)
    return db.session.scalars(select(Callsign.callsign)).all()

def get_callsign_flight(callsign_str: str) -> Flight | None:
    cs = db.session.execute(
        select(Callsign).options(joinedload(Callsign.flights))
        .where(Callsign.callsign == callsign_str)
    ).scalar_one_or_none()
    return cs.get_current_flight() if cs else None

def get_cum_deviation_for_callsign(callsign_str: str) -> float | None:
    fl = get_callsign_flight(callsign_str)
    return fl.deviation.cumulative if (fl and fl.deviation) else None

# Track ingest helper
def add_track(flight: Flight, position: Position, velocity: Velocity) -> None:
    # ensure flight is persistent
    if flight.id is None:
        db.session.add(flight)
        db.session.flush()

    db.session.add_all([position, velocity])
    db.session.flush()  # get ids for FK

    track = Track(flight=flight, position=position, velocity=velocity)
    db.session.add(track)
    db.session.commit()

# Cycle flights: close current and open new current
def cycle_flights() -> None:
    all_callsigns = db.session.scalars(select(Callsign)).all()

    for cs in all_callsigns:
        current = cs.get_current_flight()
        if current:
            # Rename and close current
            existing = len(cs.flights)
            current.name = f"flight{existing - 1 if current.name == 'currentflight' else existing}"
            current.is_current = False
            # Optional: stamp end_time if not set
            if current.end_time is None:
                from datetime import datetime, timezone
                current.end_time = datetime.now(timezone.utc)

        # Open a new current flight
        new_f = Flight(name="currentflight", is_current=True, callsign=cs)
        new_f.deviation = Deviation(cumulative=0.0, recent=0.0)
        db.session.add(new_f)

    db.session.commit()
