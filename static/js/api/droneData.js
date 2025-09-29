// static/js/api/droneData.js

// Global state store (if not already set)
window.droneData ??= {};           // per callsign: array of track points
window.lastDroneFetch ??= null;    // ISO timestamp string

/**
 * Fetch drone track data since the last known timestamp.
 * Updates `window.droneData` and `window.lastDroneFetch`
 *
 * @param {Array<string>} callsigns - List of drone call signs to fetch
 * @returns {Promise<void>}
 */
export async function fetchDroneData(callsigns) {
  if (!Array.isArray(callsigns) || !callsigns.length) return;

  var since = window.lastDroneFetch || new Date(0).toISOString();

  try {
    console.log("Sending since:", since, "window.lastDroneFetch:", window.lastDroneFetch);
    const res = await fetch('/data/since', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ callsigns, since })
    });

    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    
    var result = await res.json();


    let newestTimestamp = window.lastDroneFetch ? new Date(window.lastDroneFetch) : new Date(0);

    var data = result.data || {};

    for (var [cs, tracks] of Object.entries(data)) {
      if (!Array.isArray(tracks)) continue;

      // Initialize if needed
      window.droneData[cs] ??= [];
      
      // Append new tracks
      for (const track of tracks) {
        const ts = new Date(track.time_measured + "Z");
        if (ts > newestTimestamp) {
          newestTimestamp = ts;
        }
        window.droneData[cs].push(track);
      }
    }

    window.lastDroneFetch = newestTimestamp.toISOString();

  } catch (err) {
    console.error('Failed to fetch drone data:', err);
  }
}

