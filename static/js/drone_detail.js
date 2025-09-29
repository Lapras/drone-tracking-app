// static/js/drone_detail.js
import {
  parsePoint,
  initAirspeedAltitudeGraph, extendAirspeedAltitudeGraph,
  initDeviationGraph, extendDeviationGraph,
  initCumulativeDevGraph, extendCumulativeDevGraph
} from './utils/graphUtils.js';

import { fetchDroneData } from './api/droneData.js';

const callSign = window.callSign;

// --- DOM counters ---
function updateDroneCounters(d) {
  document.getElementById('ctr1-airspeed').textContent = (d.velocity.airspeed * 1.94384).toFixed(2);
  document.getElementById('ctr1-altitude').textContent  = d.position.altitude.toFixed(0);
  document.getElementById('ctr2-dev').textContent       = d.deviation.toFixed(2);
  document.getElementById('ctr3-cum').textContent       = d.cumulative_dev_sum.toFixed(2);
}

// --- Init empty plots ---
initAirspeedAltitudeGraph('graph1', `Airspeed & Altitude — ${callSign}`);
initDeviationGraph('graph2', 'Deviation (ft)');
initCumulativeDevGraph('graph3', 'Cumulative Deviation ≥ 25 ft');

// --- Track how many points we've displayed ---
let counter = 0;

// --- Poll new data using /data/since ---
async function pollDroneData() {
  try {
    // Fetch new tracks for this callsign
    await fetchDroneData([callSign]);

    // Get the data from the global store
    const arr = window.droneData[callSign] || [];
    if (!arr.length) return;

    // Only process new points since last counter
    const newPts = arr.slice(counter).map(parsePoint);

    extendAirspeedAltitudeGraph('graph1', newPts);
    extendDeviationGraph('graph2', newPts);
    extendCumulativeDevGraph('graph3', newPts);

    if (newPts.length) updateDroneCounters(arr.at(-1));
    counter = arr.length;

  } catch (err) {
    console.error('Error fetching drone data:', err);
  }
}

// --- Initial fetch and poll every second ---
pollDroneData();
setInterval(pollDroneData, 1000);
