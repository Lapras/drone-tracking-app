// static/js/homepage_graphs.js
import { fetchDroneData } from './api/droneData.js';
import {
  parsePoint,
  initAirspeedAltitudeGraph,
  extendAirspeedAltitudeGraph
} from './utils/graphUtils.js';

const droneList = window.droneCallSigns;
const graphState = {};

function updateHomepageCounters(cs, sp, alt) {
  document.getElementById(`ctr-${cs}-airspeed`).textContent = sp.toFixed(2);
  document.getElementById(`ctr-${cs}-altitude`).textContent = alt.toFixed(0);
}

// --- Init ---
droneList.forEach(cs => {
  initAirspeedAltitudeGraph(`graph-home-${cs}`, `Airspeed & Altitude — ${cs}`);
  graphState[cs] = { counter: 0 };
});

// --- Load history + polling ---
(async function start() {
  await fetchDroneData(droneList);

  droneList.forEach(cs => {
    const pts = (window.droneData[cs] || []).map(parsePoint);
    const result = extendAirspeedAltitudeGraph(`graph-home-${cs}`, pts);
    if (result) updateHomepageCounters(cs, result.lastSpeed, result.lastAlt);
    graphState[cs].counter += pts.length;
  });

  setInterval(async () => {
    await fetchDroneData(droneList);

    droneList.forEach(cs => {
      const raw = window.droneData[cs] || [];
      const newPts = raw.slice(graphState[cs].counter).map(parsePoint);
      const result = extendAirspeedAltitudeGraph(`graph-home-${cs}`, newPts);
      if (result) updateHomepageCounters(cs, result.lastSpeed, result.lastAlt);
      graphState[cs].counter += newPts.length;
    });
  }, 1000);
})();
