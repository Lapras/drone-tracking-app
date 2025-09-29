// static/js/layers/droneLayer.js
import { planeIcon, bearingFlat } from "../utils/mapUtils.js";

/**
 * Manages drone markers + path line on a Leaflet map
 */
export class DroneLayer {
  constructor(map, color = "darkblue") {
    this.map = map;
    this.pathLine = L.polyline([], { color, weight: 3 }).addTo(map);
    this.marker = null;
    this.prevPt = null;
  }

  update(droneId, trackPoints) {
    if (!Array.isArray(trackPoints) || trackPoints.length === 0) return;

    const coords = trackPoints.map(d => [d.position.latitude, d.position.longitude]);
    this.pathLine.setLatLngs(coords);

    const pkt = trackPoints[trackPoints.length - 1];
    const lat = pkt.position.latitude;
    const lng = pkt.position.longitude;

    const hdg = this.prevPt ? bearingFlat(this.prevPt, { lat, lng }) : 0;
    this.prevPt = { lat, lng };

    if (!this.marker) {
      this.marker = L.marker([lat, lng], {
        icon: planeIcon,
        rotationAngle: hdg,
        rotationOrigin: "center center"
      })
      .addTo(this.map)
      .bindPopup(`Drone ${droneId}`);
    } else {
      this.marker
        .setLatLng([lat, lng])
        .setRotationAngle(hdg)
        .getPopup().setContent(`Drone ${droneId}<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }

    return { lat, lng, hdg };
  }
}
