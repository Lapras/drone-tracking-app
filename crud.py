# crud.py
from __future__ import annotations
from typing import Optional, Iterable
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database import db, Callsign, Flight, Deviation, Track, Position, Velocity

# -------- Callsigns --------

def create_callsign_with_current_flight(callsign: str, airframe: Optional[str] = None) -> Callsign:
    cs = Callsign(callsign=callsign, airframe=airframe)
    db.session.add(cs)
    db.session.flush() #assigns cs.id

    current = Flight(
        name="currentflight",
        is_current=True,
        callsign=cs,
        start_time=datetime.now(timezone.utc),
    )
    current.deviation = Deviation(cumulative=0.0, recent=0.0)
    db.session.add(current)

    db.session.commit()
    return cs

def get_callsigns() -> list[str]:
    return db.session.scalars(select(Callsign.callsign)).all()

def get_callsign_flight(callsign_str: str) -> Optional[Flight]:
    cs = db.session.execute(
        select(Callsign).options(joinedload(Callsign.flights))
        .where(Callsign.callsign == callsign_str)
    ).scalar_one_or_none()
    return cs.get_current_flight() if cs else None

def get_cum_deviation_for_callsign(callsign_str: str) -> Optional[float]:
    fl = get_callsign_flight(callsign_str)
    return fl.deviation.cumulative if (fl and fl.deviation) else None

# -------- Tracks / Telemetry-ish --------

def add_track(flight: Flight, position: Position, velocity: Velocity) -> None:
    if flight.id is None:
        db.session.add(flight)
        db.session.flush()
    db.session.add_all([position, velocity])
    db.session.flush()
    db.session.add(Track(flight=flight, position=position, velocity=velocity))
    db.session.commit()

# -------- Flight cycling --------

def cycle_flights() -> None:
    all_callsigns = db.session.scalars(select(Callsign)).all()
    now = datetime.now(timezone.utc)

    for cs in all_callsigns:
        current = cs.get_current_flight()
        if current:
            # close and rename current
            existing = len(cs.flights)
            current.name = f"flight{existing - 1 if current.name == 'currentflight' else existing}"
            current.is_current = False
            if current.end_time is None:
                current.end_time = now

        new_f = Flight(name="currentflight", is_current=True, callsign=cs, start_time=now)
        new_f.deviation = Deviation(cumulative=0.0, recent=0.0)
        db.session.add(new_f)

    db.session.commit()
