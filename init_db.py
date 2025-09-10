from database import db, Callsign, Flight
from app import app  # Import your Flask app

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base class for declarative models

flight_paths = {
    "DUSKY27":       "Disaster_City_Survey_V2_converted.xlsx",
    "DUSKY18":     "RELLIS_NORTH_-_REL→Hearne_converted.xlsx",
    "DUSKY24":  "RELLIS_SOUTH_-_REL_→_AggieFarm_converted.xlsx",
    "DUSKY21":    "RELLIS_WEST_-_REL_→_Caldwell_converted.xlsx"
}


# Set up the SQLite database engine
with app.app_context():
    db.create_all()

    flight27 = Flight(name="Flight1")
    flight28 = Flight(name="Flight1")
    flight24 = Flight(name="Flight1")
    flight21 = Flight(name="Flight1")

    # Create the 4 callsign entries
    callsigns_to_add = [
        Callsign(callsign="DUSKY27", airframe="NA", flights=[flight27]),
        Callsign(callsign="DUSKY28", airframe="NA", flights=[flight28]),
        Callsign(callsign="DUSKY24", airframe="NA", flights=[flight24]),
        Callsign(callsign="DUSKY21", airframe="NA", flights=[flight21])
    ]

    for cs in callsigns_to_add:
        existing = db.session.query(Callsign).filter_by(callsign=cs.callsign).first()
        if not existing:
            db.session.add(cs)
        else:
            print(f"Callsign {cs.callsign} already exists, skipping...")



    # Commit the session to the database
    db.session.commit()

    # Confirm insertion
    print("4 Callsign entries have been added.")

    # Close the session
    db.session.close()
