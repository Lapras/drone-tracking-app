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
