// static/js/utils/graphUtils.js

/** Shared helper: time window */
export function windowStart(dt) {
  return new Date(dt.getTime() - 60_000);
}

/** Parse a raw telemetry object into plotting values */
export function parsePoint(d) {
  return {
    time: new Date(d.time_measured),
    airspeed: d.velocity.airspeed * 1.94384,   // m/s → knots
    altitude: d.position.altitude,
    deviation: d.deviation,
    cumDev: d.cumulative_dev_sum ?? 0
  };
}

/* ------------------------
   Airspeed & Altitude Graph
------------------------- */
export function initAirspeedAltitudeGraph(elementId, title) {
  Plotly.newPlot(elementId, [
    { x: [], y: [], mode: 'lines', name: 'Airspeed (knots)' },
    { x: [], y: [], mode: 'lines', name: 'Altitude (ft)', yaxis: 'y2' }
  ], {
    title,
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.2, yanchor: 'top' },
    margin: { t: 60, b: 70 },
    xaxis: { type: 'date', range: [windowStart(new Date()), new Date()], rangeslider: { visible: true } },
    yaxis: { title: 'Airspeed (knots)' },
    yaxis2: { title: 'Altitude (ft)', overlaying: 'y', side: 'right' }
  });
}

export function extendAirspeedAltitudeGraph(elementId, pts) {
  if (!pts.length) return;
  const times = pts.map(p => p.time);
  const spds  = pts.map(p => p.airspeed);
  const alts  = pts.map(p => p.altitude);

  Plotly.extendTraces(elementId, { x: [times, times], y: [spds, alts] }, [0, 1]);

  const last = times.at(-1);
  Plotly.relayout(elementId, { 'xaxis.range': [windowStart(last), last] });

  return { lastSpeed: spds.at(-1), lastAlt: alts.at(-1) };
}

/* ------------------------
   Deviation Graph
------------------------- */
export function initDeviationGraph(elementId, title) {
  Plotly.newPlot(elementId, [
    { x: [], y: [], type: 'bar', marker: { color: [] } }
  ], {
    title,
    xaxis: { type: 'date', range: [windowStart(new Date()), new Date()], rangeslider: { visible: true } },
    yaxis: { title: 'Deviation (ft)' }
  });
}

export function extendDeviationGraph(elementId, pts) {
  if (!pts.length) return;
  const times = pts.map(p => p.time);
  const devs  = pts.map(p => p.deviation);
  const cols  = devs.map(v => v > 25 ? 'red' : 'blue');

  Plotly.extendTraces(elementId, { x: [times], y: [devs], 'marker.color': [cols] }, [0]);

  const last = times.at(-1);
  Plotly.relayout(elementId, { 'xaxis.range': [windowStart(last), last] });
}

/* ------------------------
   Cumulative Deviation Graph
------------------------- */
export function initCumulativeDevGraph(elementId, title) {
  Plotly.newPlot(elementId, [
    { x: [], y: [], mode: 'lines+markers', name: 'Cumulative Deviation' }
  ], {
    title,
    xaxis: { type: 'date', range: [windowStart(new Date()), new Date()], rangeslider: { visible: true } },
    yaxis: { title: 'Total (ft)' }
  });
}

export function extendCumulativeDevGraph(elementId, pts) {
  if (!pts.length) return;
  const times = pts.map(p => p.time);
  const cum   = pts.map(p => p.cumDev);

  Plotly.extendTraces(elementId, { x: [times], y: [cum] }, [0]);

  const last = times.at(-1);
  Plotly.relayout(elementId, { 'xaxis.range': [windowStart(last), last] });
}
