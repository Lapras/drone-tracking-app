// static/js/splitmap.js
import { addBaseLayer } from "./utils/mapUtils.js";
import { DroneLayer } from "./layers/droneLayer.js";
import { fetchDroneData } from "./api/droneData.js";

document.addEventListener("DOMContentLoaded", function () {
  const defaultCenter = [27.7123, -97.3246];
  const defaultZoom = 14;
  const pollInterval = 2000;

  const mapAll = addBaseLayer(L.map("map-all").setView(defaultCenter, defaultZoom));
  const mapSingle = addBaseLayer(L.map("map-single").setView(defaultCenter, defaultZoom));

  const droneLayersAll = {};    // per drone on overview map
  const droneLayerSingle = new DroneLayer(mapSingle, "crimson");

  let selectedCallSign = null;
  const labelEl = document.getElementById("zoomed-drone-label");

  function setFocusedDrone(cs) {
    selectedCallSign = cs;
    if (labelEl) labelEl.textContent = cs ? `Zoomed drone: ${cs}` : "Zoomed drone: —";
    droneLayerSingle.pathLine.setLatLngs([]);
  }

  // Build summary list
  const container = document.getElementById("drone-data-container");
  window.droneCallSigns.forEach((cs, i) => {
    const el = document.createElement("div");
    el.className = "drone-summary";
    el.id = "summary-" + cs;
    el.style.cursor = "pointer";
    el.innerHTML = `<strong>${cs}</strong><br><span id="pos-${cs}">--</span>`;

    el.onclick = () => {
      document.querySelectorAll(".drone-summary").forEach(d => d.classList.remove("selected"));
      el.classList.add("selected");
      setFocusedDrone(cs);
    };

    container.appendChild(el);
    if (i === 0) {
      el.classList.add("selected");
      setFocusedDrone(cs);
    }
  });

  async function fetchAndUpdateAll() {
    try {
      await fetchDroneData(window.droneCallSigns);
      const boundsGroup = [];

      for (const cs of window.droneCallSigns) {
        const history = window.droneData[cs] || [];
        if (!history.length) continue;

        // Update "all drones" map
        droneLayersAll[cs] ??= new DroneLayer(mapAll, "darkblue");
        const { lat, lng } = droneLayersAll[cs].update(cs, history);
        boundsGroup.push(droneLayersAll[cs].marker);

        const posEl = document.getElementById("pos-" + cs);
        if (posEl) posEl.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;

        // Update single drone map if focused
        if (cs === selectedCallSign) {
          droneLayerSingle.update(cs, history);
          mapSingle.panTo([lat, lng], { animate: false });
        }
      }

      if (boundsGroup.length) {
        const group = L.featureGroup(boundsGroup);
        mapAll.fitBounds(group.getBounds().pad(0.2));
      }
    } catch (err) {
      console.error("fetchAndUpdateAll error:", err);
    }
  }

  fetchAndUpdateAll();
  setInterval(fetchAndUpdateAll, pollInterval);
});
