#!/usr/bin/env python3
"""
simulate_and_send.py

This script generates random telemetry for four predefined drones and POSTs each packet 
to the specified endpoint (https://ashtonrwsmith.pythonanywhere.com/data). It loops indefinitely,
sending one update per drone each second.

Requirements:
    pip install requests

Usage:
    python3 simulate_and_send.py
"""

import time
import random
import requests
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

# Configuration
ENDPOINT_URL = "http://localhost:8000/data"
API_KEY = os.getenv("API_KEY")

# List of the four drones
DRONES = [
    "DUSKY21",
    "DUSKY27",
    "DUSKY28",
    "DUSKY24"
]

#geographic bounding box for random positions (example: around College Station, TX)
LAT_CENTER = 30.6280
LON_CENTER = -96.3344
LAT_SPAN = 0.02  # ~1.2 miles
LON_SPAN = 0.02  # ~1.2 miles

session = requests.Session()
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}

def generate_random_packet(call_sign):
    """
    generate random telemetry packet for given call_sign
    """
    latitude = LAT_CENTER + (random.random() - 0.5) * LAT_SPAN
    longitude = LON_CENTER + (random.random() - 0.5) * LON_SPAN
    altitude = random.uniform(100, 300)  # altitude between 100 and 300 ft
    airspeed = random.uniform(10, 60)    # airspeed between 10 and 60 m/s

    packet = {
        "call_sign": call_sign,
        "position": {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "altitude": round(altitude, 2)
        },
        "velocity": {
            "airspeed": round(random.uniform(0, 50), 2),
            "ground_speed": round(random.uniform(0, 50), 2),
            "vertical_speed": round(random.uniform(-10, 10), 2),
            "units_speed": "MetersPerSecond",
            "track": round(random.uniform(0, 360), 2)
        },
        "time_measured": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        # "orientation": {
        #     "pitch": round(random.uniform(-30, 30), 2),
        #     "roll": round(random.uniform(-30, 30), 2),
        #     "yaw": round(random.uniform(0, 360), 2),
        #     "pitch_rate": round(random.uniform(-5, 5), 2),
        #     "roll_rate": round(random.uniform(-5, 5), 2),
        #     "yaw_rate": round(random.uniform(-5, 5), 2)
        # }
    }
    return packet

def send_packet(packet):
    """
    Send a single telemetry packet to the endpoint.
    """
    try:
        resp = session.post(ENDPOINT_URL, json=packet, headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[{packet['call_sign']}] Sent at {packet['time_measured']}")
        else:
            print(f"[ERROR {resp.status_code}] {resp.text}")
    except session.RequestException as e:
        print(f"[EXCEPTION] Failed to send {packet['call_sign']}: {e}")

def main():
    print("Starting telemetry simulation. Press Ctrl+C to stop.")
    while True:
        for call_sign in DRONES:
            pkt = generate_random_packet(call_sign)
            send_packet(pkt)
            # time.sleep(0.25)  # stagger 4 updates evenly within each second
        # Ensure roughly 1-second intervals between each 4-drone batch

if __name__ == "__main__":
    main()

