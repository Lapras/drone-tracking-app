from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import logging
from db import *

views = Blueprint(__name__, "views")

@views.route("/") 
def home(): # Remember that def means defining a function, i.e. home
    # Renders our index.html file in the templates folder for the home page
    # You can put as many var.'s in the return as you want, they can be gotten from the webpage from there
    app.logger.debug("TESTING")
    callsigns = Callsign.query.all()
    return render_template("index.html", drones=sorted([callsigns]))

@views.route("/drone/<call_sign>")
def drone_page(call_sign):
    app.logger.info("TESTING 123\n")
    callsigns = Callsign.query.all()
    if call_sign not in available_callsigns:
        return render_template("404.html"), 404  # Or redirect to home if preferred

    #drones = sorted(ALLOWED_CALLSIGNS)  # Optional: for dropdown
    return render_template("droneJ.html", call_sign=call_sign, drones=available_callsigns)

# ---- JSON ingest ----
# Simulator sends:
# {
#   "call_sign": "...",
#   "position": {"latitude": ..., "longitude": ..., "altitude": ...},
#   "velocity": {"airspeed": ...},
#   "time_measured": "2025-09-11T00:00:00Z"
# }

'''
@views.route("/data", methods=["POST"])
def data_ingest():
    api_key = request.headers.get("X-API-KEY")
    expected = current_app.config.get("INGEST_API_KEY")
    if expected and api_key != expected:
        return jsonify({"error": "Unauthorized"}), 401

    p = request.get_json(silent=True) or {}
    call_sign = p.get("call_sign")
    pos = p.get("position") or {}
    vel = p.get("velocity") or {}

    if not call_sign or "latitude" not in pos or "longitude" not in pos:
        return jsonify({"error": "Invalid payload"}), 400

    fl = get_callsign_flight(call_sign)
    if not fl:
        return jsonify({"error": f"Unknown call_sign '{call_sign}'"}), 400

    # Parse timestamp if provided
    ts = p.get("time_measured")
    ts_dt = None
    if ts:
        try:
            ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            ts_dt = None

    # Insert position + track with minimal overhead
    add_track_fast(
        flight_id=fl.id,
        latitude=pos.get("latitude"),
        longitude=pos.get("longitude"),
        altitude=pos.get("altitude") or 0.0,
        v_air=vel.get("airspeed"),
        v_ground=vel.get("groundspeed"),
        v_vert=vel.get("vertspeed"),
        v_units=vel.get("units"),
        ts=ts_dt,
    )

    # Optional: deviation math (cheap, O(1) per packet if path cached)
    # Only do this if you actually need the metric in real time.
    delta_ft = 0.0
    if LineString and call_sign in path_cache and pos.get("latitude") is not None and pos.get("longitude") is not None:
        pt = Point(pos["longitude"], pos["latitude"])
        line = path_cache[call_sign]
        nearest = line.interpolate(line.project(pt))
        # quick lat/lon planar approx in meters
        dist_m = pt.distance(nearest) * 111_000
        dist_ft = dist_m * 3.28084
        if dist_ft > 25.0:
            delta_ft = dist_ft - 25.0
            bump_cum_deviation_fast(fl.id, delta_ft)

    db.session.commit()  # single commit for both insert(s) and deviation bump

    return jsonify({"message": "ok", "delta_deviation_ft": round(delta_ft, 2)}), 200


'''