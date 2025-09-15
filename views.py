#-----SET UP/INIT----------------------------------------------------------------------------------------------------------------#

# This allows us to de-clutter the app.py page by putting our different links and pages
# 'render_template' is the package that helps us view the html files in templates folder
# Request helps us handle queries like .../profile?name=Joe
# Jsonify helps us return our JSON and handle it when it comes in
# Redirect and url_for help redirect users to other pages
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
import random

from collections import defaultdict
import os
import pandas as pd
from shapely.geometry import LineString, Point

from dotenv import load_dotenv

import database

# Load environment variables from .env file
load_dotenv()
# Get the API key from the environment
API_KEY = "TESTKEY"


views = Blueprint(__name__, "views") # Init/create the Blueprint and call it views

# # ——— FLIGHT PATH CONFIG ———
FLIGHT_XLSX_DIR = "./flight_path_data"

flight_paths = {
    "DUSKY27":       "Disaster_City.xlsx",
    "DUSKY18":     "Rellis_North.xlsx",
    "DUSKY24":  "Rellis_South.xlsx",
    "DUSKY21":    "Rellis_West.xlsx"
}

# Preload LineStrings for each flight path
path_lines = {}
for name, xlsx in flight_paths.items():
    full_path = os.path.join(FLIGHT_XLSX_DIR, xlsx)
    df = (pd.read_excel(full_path, sheet_name="in")
            [["Latitude", "Longitude", "Altitude"]]
            .dropna()
            .reset_index(drop=True))
    coords = list(zip(df["Longitude"], df["Latitude"]))
    path_lines[name] = LineString(coords)



#-----HOME PAGE---------------------------------------------------------------------------------------------------------------------#

@views.route("/") 
def home(): # Remember that def means defining a function, i.e. home
    # Renders our index.html file in the templates folder for the home page
    # You can put as many var.'s in the return as you want, they can be gotten from the webpage from there
    callsigns = database.get_callsigns()
    return render_template("index.html", drones=sorted(callsigns))

#-----DRONE TAKING JSON INPUT------------------------------------------------------------------------------------------------------#
# This will be drone J for JSON, it will take in user inputted json through a curl
# request, store it in a variable, then push it to a screen like the other drones
@views.route("/drone/<call_sign>")
def drone_page(call_sign):
    callsigns = database.get_callsigns()
    if call_sign not in callsigns:
        return render_template("404.html"), 404  # Or redirect to home if preferred

    #drones = sorted(ALLOWED_CALLSIGNS)  # Optional: for dropdown
    return render_template("droneJ.html", call_sign=call_sign, drones=callsigns)

# #-----BACKEND PAGES-------------------------------------------------------------------------------------------------------------------#

# This will take in JSON data and then post it on the /data page
# Use the testFile.py file to see if the site can get a JSON POST request
# Define your secret key securely in production
#API_KEY = "your-secret-api-key"  
@views.route("/data", methods=["GET", "POST"])
def data_route():
    if request.method == "POST":
        return post_data(request)
    elif request.method == "GET":
        return get_data()

    

def get_data():
    return render_template("displayJSON.html", data=latest_json, drones=ALLOWED_CALLSIGNS)

def post_data(request):
    client_key = request.headers.get("X-API-KEY")
    if client_key != current_app.config["API_KEY"]:
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 401
    data_json = request.get_json()
    if not data_json:
        return jsonify({"error": "No JSON data received"}), 400
    call_sign = data_json.get("call_sign")
    callsigns = database.get_callsigns()
    if(call_sign not in callsigns):
        return jsonify({"error": "Incorrect callsign"}), 400
    
    pos_data = data_json.get("position", {})
    velocity_data = data_json.get("velocity", {})
    lat = pos_data.get("latitude")
    lon = pos_data.get("longitude")
    alt = pos_data.get("altitude", 0.0)

    flightDeviation = database.get_cum_deviation_for_callsign(call_sign)

    flight = database.get_callsign_flight(call_sign)

    # Compute deviation from path
    if call_sign in path_lines and lat is not None and lon is not None:
        pt = Point(lon, lat)
        line = path_lines[call_sign]
        nearest = line.interpolate(line.project(pt))
        dist_m = pt.distance(nearest) * 111000
        dist_ft = dist_m * 3.28084
        deviation = round(dist_ft, 2)

        # Accumulate deviation sum over 25 ft
        if deviation > 25:
            flightDeviation += (deviation - 25)
            
        flightDeviation = round(deviation, 2)
    position = database.Position(latitude=lat, longitude=lon, altitude=alt)
    # Yes, i know verticle is a typo, but it's in the json_data folder so im abding by it for now
    velocity = database.Velocity(airspeed = velocity_data.get(""), ground_speed = velocity_data.get(""), vertical_speed = velocity_data.get("verticle_speed"), units_speed = velocity_data.get("units_speed"))

    database.add_track(flight, position, velocity)

    database.commit_session()

    return jsonify({"message": "JSON received and deviation calculated"}), 200

#Gets data for each callsign at /data/callsign
#will give error if no callsign at page

@views.route("/data/<call_sign>", methods=["GET"])
def data_by_callsign(call_sign):
    flight = database.get_callsign_flight(call_sign)

    sorted_tracks = sorted(flight.tracks, key=lambda t: t.timestamp)

    data_list = []
    for track in sorted_tracks:
        position = track.position
        data_list.append({
            "timestamp": track.timestamp.isoformat(),
            "position": {
                "latitude": position.latitude,
                "longitude": position.longitude,
                "altitude": position.altitude,
            },
            "velocity_airspeed": track.velocity.airspeed,
            "velocity_groundSpeed": track.velocity.ground_speed,
            "velocity_vertSpeed": track.velocity.vertical_speed,
            "velocity_unitsSpeed": track.velocity.units_speed,
        })

    return jsonify(data_list), 200

#clear history button
@views.route("/reset_history", methods=["POST"])
def reset_history():
    database.cycle_flights()
    return redirect(url_for("views.home"))

# #------------------------------------------------------------------------------------------------------------------------------------#
