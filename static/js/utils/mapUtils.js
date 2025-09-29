// static/js/utils/mapUtils.js

// Plane icon for all maps
export const planeIcon = L.icon({
  iconUrl: '/static/images/plane-icon.png',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16]
});

// Tile layer helper
export function addBaseLayer(map) {
  const tileUrl = 'https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=jU54ne5D7wcPIuhFGLb4';
  const tileOpts = { attribution: '&copy; <a href="https://www.openmaptiles.org/">OpenMapTiles</a> contributors' };
  L.tileLayer(tileUrl, tileOpts).addTo(map);
  return map;
}

// Flat-earth bearing between two points
export function bearingFlat(p1, p2) {
  const toRad = d => d * Math.PI / 180;
  const toDeg = r => r * 180 / Math.PI;
  const φ1 = toRad(p1.lat),
        φ2 = toRad(p2.lat),
        dLat = φ2 - φ1,
        dLon = toRad(p2.lng - p1.lng) * Math.cos((φ1 + φ2) / 2);
  return (toDeg(Math.atan2(dLon, dLat)) + 360) % 360;
}
