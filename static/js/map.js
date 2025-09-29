// static/js/map.js
import { addBaseLayer } from "./utils/mapUtils.js";
import { DroneLayer } from "./layers/droneLayer.js";
import { fetchDroneData } from "./api/droneData.js";

const callSign = window.callSign || window.droneCallSigns?.[0];
const map = addBaseLayer(L.map("map").setView([27.7123, -97.3246], 14));

const droneLayer = new DroneLayer(map, "crimson");  // only one drone

async function refreshDrone() {
  if (!callSign) return;

  try {
    const prevLen = (window.droneData[callSign]?.length) || 0;
    await fetchDroneData([callSign]);
    const history = window.droneData[callSign] || [];
    if (history.length <= prevLen) return; // no new points

    const newPts = history.slice(prevLen);
    droneLayer.update(callSign, newPts);

   const { latitude: lat, longitude: lng } = newPts.at(-1).position;
    map.panTo([lat, lng], { animate: false });


  } catch (err) {
    console.error("refreshDrone error:", err);
  }
}

async function initialLoad() {
  if (!callSign) return;

  // Temporarily store the original lastDroneFetch
  const origSince = window.lastDroneFetch;

  // Force fetch everything
  window.lastDroneFetch = null;
  await fetchDroneData([callSign]);

  const history = window.droneData[callSign] || [];
  if (history.length) {
    const prevLen = 0;
    const newPts = history.slice(prevLen);
    droneLayer.update(callSign, history);
    const { latitude: lat, longitude: lng } = newPts.at(-1).position;
    map.setView([lat, lng], 14);
  }
}


// Initial load + interval
initialLoad();
setInterval(refreshDrone, 1000);
