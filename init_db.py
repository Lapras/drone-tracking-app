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

# Set up the SQLite database engine
engine = create_engine('sqlite:///instance/drone_app.db', echo=True)

# Create the tables in the database (if they don't already exist)
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create the 4 callsign entries
callsigns = [
    Callsign(callsign="Alpha1", airframe="Drone A1"),
    Callsign(callsign="Bravo2", airframe="Drone B2"),
    Callsign(callsign="Charlie3", airframe="Drone C3"),
    Callsign(callsign="Delta4", airframe="Drone D4")
]

# Add the callsigns to the session
session.add_all(callsigns)

# Commit the session to the database
session.commit()

# Confirm insertion
print("4 Callsign entries have been added.")

# Close the session
session.close()
