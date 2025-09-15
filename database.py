from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, text
from sqlalchemy import Integer
from sqlalchemy import create_engine, inspect, Table, MetaData, text
from sqlalchemy import Column
from sqlalchemy.types import Integer, Float, String, DateTime, LargeBinary, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


from typing import List
from datetime import datetime, timezone

import os, re
import pandas as pd


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Callsign(db.Model):
    __tablename__ = "callsigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    callsign: Mapped[str] = mapped_column(unique=True, nullable=False)
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

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(default=0.0, nullable=False)

    flight_id = mapped_column(ForeignKey("flights.id"), nullable=False)

class Flight(db.Model):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    # start_time = Mapped[datetime]

    callsign_id = mapped_column(ForeignKey("callsigns.id"), nullable=False)
    callsign = relationship(Callsign, back_populates="flights")

    tracks: Mapped[List["Track"]] = relationship(back_populates="flight")

    deviation: Mapped["CumulativeDeviation"] = relationship("CumulativeDeviation", uselist=False)

    def __init__(self, name):
        self.name = name
        self.deviation = CumulativeDeviation()

class Track(db.Model):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)

    flight_id = mapped_column(ForeignKey("flights.id"), nullable=False)
    flight = relationship("Flight", back_populates="tracks")

    position_id = mapped_column(ForeignKey("positions.id"), nullable=False)
    position: Mapped["Position"] = relationship("Position", uselist=False)

    velocity_id = mapped_column(ForeignKey("velocities.id"), nullable=False)
    velocity: Mapped["Velocity"] = relationship("Velocity", uselist=False)

    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

class Position(db.Model):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)

    latitude: Mapped[float] = mapped_column(default=0.0)
    longitude: Mapped[float]    = mapped_column(default=0.0)
    altitude: Mapped[float] = mapped_column(default=0.0)

class Velocity(db.Model):
    __tablename__ = "velocities"

    id: Mapped[int] = mapped_column(primary_key=True)

    airspeed: Mapped[float] = mapped_column(default=0.0)
    ground_speed: Mapped[float] = mapped_column(default=0.0)
    vertical_speed: Mapped[float] = mapped_column(default=0.0)
    units_speed: Mapped[str] = mapped_column(default="MetersPerSecond")


class ExpectedPosition(db.Model):
    __tablename__ = "expectedpositions"
    id: Mapped[int] = mapped_column(primary_key=True)

    position_id = mapped_column(ForeignKey("positions.id"), nullable=False)
    poisition: Mapped["Position"] = relationship("Position", uselist=False)

    flight_id = mapped_column(ForeignKey("flightplans.id"))

    order: Mapped[int] = mapped_column(nullable=False)

class FlightPlan(db.Model):
    __tablename__ = "flightplans"

    id: Mapped[int] = mapped_column(primary_key=True)

    expected_positions: Mapped[List["ExpectedPosition"]] = relationship("ExpectedPosition")

def create_all():
    db.create_all()

def get_callsigns():
    result = db.session.execute(text("SELECT callsign FROM callsigns")).fetchall()
    callsigns = db.session.execute(db.select(Callsign.callsign)).scalars().all()
    return callsigns

def get_callsign_flight(callsign_str):
    callsign = db.session.query(Callsign).filter_by(callsign=callsign_str).first()
    if callsign:
        return callsign.get_current_flight()

def get_cum_deviation_for_callsign(callsign_str):
    callsign = db.session.query(Callsign).filter_by(callsign=callsign_str).first()
    if callsign:
        return callsign.get_current_flight().deviation.amount

def add_track(flight, position, velocity):
    db.session.add(position)
    db.session.add(velocity)

    track = Track(
        flight_id=flight.id,
        position = position, 
        velocity = velocity
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

def excel_to_db(
    excel_name: str | None = None,
    db_dest: str = "instance/drone_app.db",
    table_name: str | None = None,
    sheet=0,
    mode: str = "create",  # "create", "replace", or "append"
    order: bool = False
):
    if excel_name is None:
        excel_name = str(input("What is the excel filename? "))
    if not os.path.exists(excel_name):
        raise FileNotFoundError(f"Excel file not found: {excel_name}")

    # ---- Read Excel ----
    df = pd.read_excel(excel_name, sheet_name=sheet, header=0)
    if df.empty:
        raise ValueError("The Excel sheet is empty.")

    # ---- CLEAN: remove 'Unnamed:*' and fully-empty columns ----
    df.columns = [str(c).strip() for c in df.columns]
    # drop Unnamed columns (Excel index/blank headers)
    mask_unnamed = pd.Series(df.columns).str.match(r'(?i)^Unnamed[:\s_]*\d*$')
    df = df.loc[:, ~mask_unnamed.values]
    # drop all-null columns
    df = df.dropna(axis=1, how='all')


    if order and ("order" not in df.columns):
        df["order"] = range(1, len(df) + 1)  # starts at 1, increments by 1


    # ---- Sanitize column names for SQLite ----
    def _safe(s: str) -> str:
        s = re.sub(r"\s+", "_", str(s).strip())
        s = re.sub(r"[^\w]", "", s)
        return f"col_{s}" if not s or s[0].isdigit() else s

    df.columns = [_safe(c) for c in df.columns]

    # ---- Default table name from file ----
    if table_name is None:
        base = os.path.splitext(os.path.basename(excel_name))[0]
        table_name = _safe(base)

    # ---- Ensure DB dir exists ----
    db_dir = os.path.dirname(db_dest)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.abspath(db_dest)

    # ---- Build engine/inspector ----
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    insp = inspect(engine)
    metadata = MetaData()

    # ---- dtype mapping ----
    def _dtype_map(pdf: pd.DataFrame):
        dtypes = {}
        for c in pdf.columns:
            s = pdf[c]
            if pd.api.types.is_integer_dtype(s):
                dtypes[c] = Integer()
            elif pd.api.types.is_bool_dtype(s):
                dtypes[c] = Boolean()
            elif pd.api.types.is_float_dtype(s):
                dtypes[c] = Float()
            elif pd.api.types.is_datetime64_any_dtype(s):
                dtypes[c] = DateTime()
            elif pd.api.types.is_string_dtype(s):
                dtypes[c] = String()
            else:
                if pd.api.types.is_object_dtype(s):
                    non_na = s.dropna()
                    if not non_na.empty and non_na.map(lambda v: isinstance(v, (bytes, bytearray))).all():
                        dtypes[c] = LargeBinary()
                    else:
                        dtypes[c] = String()
                else:
                    dtypes[c] = String()
        return dtypes

    # ---- Normalize datetimes ----
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = pd.to_datetime(df[c], errors="coerce")

    dtype = _dtype_map(df)

    # ---- Mode checks ----
    exists = insp.has_table(table_name)
    if mode not in {"create", "replace", "append"}:
        raise ValueError("mode must be 'create', 'replace', or 'append'.")

    # Replace -> drop existing first
    if mode == "replace" and exists:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        exists = False  # we're going to recreate

    # If append but table doesn’t exist, we’ll create it (like create mode)
    will_create = (mode in {"create", "replace"}) or (mode == "append" and not exists)

    # ---- If creating a NEW table, add id PK if not already present ----
    if will_create:
        # Build SQLAlchemy Table schema explicitly so we can set a PK
        columns = []
        # Add id only if not already present
        has_id = any(col == "id" for col in df.columns)
        if not has_id:
            columns.append(Column("id", Integer, primary_key=True, autoincrement=True))

        for col in df.columns:
            sa_type = dtype[col]
            # if user already has an 'id' column, we do NOT force PK—leave as-is
            columns.append(Column(col, sa_type))

        tbl = Table(table_name, metadata, *columns)
        # Actually create the table
        metadata.create_all(bind=engine, tables=[tbl])

    # ---- Validate schema before append mode ----
    if mode == "append" and exists:
        existing_cols = [col["name"] for col in insp.get_columns(table_name)]
        if existing_cols != list(insp.get_columns(table_name, table_name=table_name)) and False:
            pass  # (kept as placeholder; we rely on create/append consistency)
        # Enforce same order & names (excluding auto id if present)
        existing_cols = [col["name"] for col in insp.get_columns(table_name)]
        # If table has auto 'id', don't require it in df
        df_cols_for_compare = list(df.columns)
        ex_cols_for_compare = [c for c in existing_cols if c != "id"]
        if ex_cols_for_compare != df_cols_for_compare:
            raise ValueError(
                "Schema mismatch during append.\n"
                f"Existing columns (excluding id): {ex_cols_for_compare}\n"
                f"Incoming columns: {df_cols_for_compare}"
            )

    # ---- Load data (always append—table was created above if needed) ----
    # If we just added an auto-PK 'id', keep it out of the DataFrame columns so SQLite autogenerates it
    if will_create and "id" not in df.columns:
        pass  # nothing to drop—df has no 'id'
    elif "id" in df.columns:
        # If user provided an 'id' column, we’ll load it as-is
        # (no change; to_sql will insert the values)
        pass

    with engine.begin() as conn:
        df.to_sql(table_name, con=conn, if_exists="append", index=False, method="multi")

    return table_name

def delete_table(table_name: str, db_name: str = "instance/drone_app.db"):
    """Delete a table in the SQLite database if it exists."""
    db_path = os.path.abspath(db_name)
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    insp = inspect(engine)

    if insp.has_table(table_name):
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        print(f"Table '{table_name}' deleted from {db_path}")
    else:
        print(f"Table '{table_name}' does not exist in {db_path}")

def db_to_excel(db_name: str = "instance/drone_app.db", output_path: str | None = None):
    """
    Export the SQLite database to an Excel file.
    Each table is written to a separate sheet named after the table.
    File is saved to the user's Downloads folder unless output_path is specified.
    """
    db_path = os.path.abspath(db_name)
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    insp = inspect(engine)

    # Default output: Downloads folder
    if output_path is None:
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads, exist_ok=True)
        base = os.path.splitext(os.path.basename(db_path))[0]
        output_path = os.path.join(downloads, f"{base}_export.xlsx")

    tables = insp.get_table_names()
    if not tables:
        print(f"No tables found in {db_path}, nothing to export.")
        return None

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for table in tables:
            df = pd.read_sql_table(table, engine)
            df.to_excel(writer, sheet_name=table, index=False)

    print(f"Database exported to Excel: {output_path}")
    return output_path


def main():
    excel_to_db(table_name="flightplans", 
                excel_name="flight_path_data/Disaster_City_Survey_V2_converted.xlsx", 
                mode="replace",
                order=True)
    
    delete_table("Flight Plans")

    db_to_excel()
    

if __name__ == "__main__":
    main()
