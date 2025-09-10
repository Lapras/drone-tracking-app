from database import db, Callsign

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base class for declarative models
Base = declarative_base()

# Define the Callsign model
class Callsign(Base):
    __tablename__ = 'callsign'

    id = Column(Integer, primary_key=True, autoincrement=True)
    callsign = Column(String, unique=True, nullable=False)
    airframe = Column(String, nullable=False)


flight_paths = {
    "DUSKY27":       "Disaster_City_Survey_V2_converted.xlsx",
    "DUSKY18":     "RELLIS_NORTH_-_REL→Hearne_converted.xlsx",
    "DUSKY24":  "RELLIS_SOUTH_-_REL_→_AggieFarm_converted.xlsx",
    "DUSKY21":    "RELLIS_WEST_-_REL_→_Caldwell_converted.xlsx"
}


# Set up the SQLite database engine
engine = create_engine('sqlite:///instance/drone_app.db', echo=True)

# Create the tables in the database (if they don't already exist)
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create the 4 callsign entries
callsigns = [
    Callsign(callsign="DUSKY27", airframe="NA"),
    Callsign(callsign="DUSKY28", airframe="NA"),
    Callsign(callsign="DUSKY24", airframe="NA"),
    Callsign(callsign="DUSKY21", airframe="NA")
]

# Add the callsigns to the session
session.add_all(callsigns)

# Commit the session to the database
session.commit()

# Confirm insertion
print("4 Callsign entries have been added.")

# Close the session
session.close()
