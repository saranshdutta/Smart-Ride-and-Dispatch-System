/* ─────────────────────────────────────────────────────────────────────────
   Smart Dispatch — Dashboard Application Logic
   ───────────────────────────────────────────────────────────────────────── */

const API_BASE = "http://127.0.0.1:8000/api";

const ALGO_META = {
  greedy:   { name: "Greedy Nearest Driver",   time: "O(P × D)",           space: "O(1)",       color: "#6366f1" },
  heap:     { name: "Heap Priority Queue",      time: "O((D + P) log D)",   space: "O(D)",       color: "#22d3ee" },
  dijkstra: { name: "Dijkstra Graph Routing",   time: "O(P·(V+E) log V)",   space: "O(V + E)",   color: "#a78bfa" },
};

const LOCATIONS = {
  delhi: { lat_min: 28.40, lat_max: 28.90, lon_min: 77.00, lon_max: 77.50, name: "Delhi NCR" },
  mumbai: { lat_min: 18.90, lat_max: 19.30, lon_min: 72.80, lon_max: 73.00, name: "Mumbai" },
  bangalore: { lat_min: 12.80, lat_max: 13.10, lon_min: 77.50, lon_max: 77.70, name: "Bengaluru" },
  chennai: { lat_min: 12.90, lat_max: 13.20, lon_min: 80.10, lon_max: 80.30, name: "Chennai" },
  kolkata: { lat_min: 22.50, lat_max: 22.70, lon_min: 88.30, lon_max: 88.50, name: "Kolkata" },
};

// ── State ────────────────────────────────────────────────────────────────
let distChart   = null;
let benchChart  = null;
let lastResult  = null;
let apiOnline   = false;
let lmap        = null;
let mapLayerGroup = null;

// ── Init ─────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  bindRangeInputs();
  bindAlgoSelect();
  bindLocationSelect();
  checkApiStatus();
  // Initialize icons for static HTML
  if (window.lucide) {
    lucide.createIcons();
  }
});

function bindRangeInputs() {
  const bind = (id, valId) => {
    const el  = document.getElementById(id);
    const val = document.getElementById(valId);
    el.addEventListener("input", () => { val.textContent = el.value; });
  };
  bind("numDrivers",    "numDriversVal");
  bind("numPassengers", "numPassengersVal");
}

function bindAlgoSelect() {
  document.getElementById("algoSelect").addEventListener("change", e => {
    const key  = e.target.value;
    const meta = ALGO_META[key] || {};
    document.getElementById("badgeAlgo").textContent = meta.name || key;
  });
}

function bindLocationSelect() {
  document.getElementById("locationSelect").addEventListener("change", e => {
    const key = e.target.value;
    const loc = LOCATIONS[key];
    document.getElementById("mapLocationBadge").textContent = loc ? loc.name : "Location";
  });
}

// ── API Health Check ──────────────────────────────────────────────────────
async function checkApiStatus() {
  try {
    const res = await fetch(`${API_BASE.replace("/api", "")}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      setApiStatus(true);
      return;
    }
  } catch (_) {}
  setApiStatus(false);
}

function setApiStatus(online) {
  apiOnline = online;
  const dot   = document.getElementById("statusDot");
  const label = document.getElementById("statusLabel");
  if (online) {
    dot.classList.add("online");
    label.textContent = "API Online";
  } else {
    dot.classList.remove("online");
    label.textContent = "API Offline";
  }
}

// ── Simulation ────────────────────────────────────────────────────────────
async function runSimulation() {
  if (!apiOnline) { showToast('<i data-lucide="alert-triangle"></i> Backend is offline. Start the API first.', "error"); return; }

  const locKey = document.getElementById("locationSelect").value;
  const loc = LOCATIONS[locKey] || LOCATIONS.delhi;

  const payload = {
    num_drivers:    parseInt(document.getElementById("numDrivers").value),
    num_passengers: parseInt(document.getElementById("numPassengers").value),
    algorithm:      document.getElementById("algoSelect").value,
    seed:           parseInt(document.getElementById("seedInput").value) || 42,
    lat_min:        loc.lat_min,
    lat_max:        loc.lat_max,
    lon_min:        loc.lon_min,
    lon_max:        loc.lon_max,
  };

  setLoading(true);

  try {
    const res  = await fetch(`${API_BASE}/simulate`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Simulation failed");
    }
    const data = await res.json();
    lastResult = data;

    renderStats(data.metrics);
    renderAlgoInfo(payload.algorithm, data.metrics);
    renderMap(data.drivers, data.passengers, data.trips);
    renderDistChart(data.trips);
    renderTripList(data.trips);

    document.getElementById("benchmarkSection").style.display = "none";
    showToast(`<i data-lucide="check-circle"></i> ${data.metrics.total_matches} matches in ${data.metrics.execution_time_ms.toFixed(2)} ms`, "success");
  } catch (err) {
    showToast(`<i data-lucide="x-circle"></i> ${err.message}`, "error");
  } finally {
    setLoading(false);
  }
}

// ── Benchmark ─────────────────────────────────────────────────────────────
async function runBenchmark() {
  if (!apiOnline) { showToast('<i data-lucide="alert-triangle"></i> Backend is offline. Start the API first.', "error"); return; }

  const d = document.getElementById("numDrivers").value;
  const p = document.getElementById("numPassengers").value;
  const s = document.getElementById("seedInput").value || 42;

  const locKey = document.getElementById("locationSelect").value;
  const loc = LOCATIONS[locKey] || LOCATIONS.delhi;

  setLoading(true);

  try {
    const url = `${API_BASE}/benchmark?num_drivers=${d}&num_passengers=${p}&seed=${s}&lat_min=${loc.lat_min}&lat_max=${loc.lat_max}&lon_min=${loc.lon_min}&lon_max=${loc.lon_max}`;
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw new Error("Benchmark request failed");
    const data = await res.json();

    renderBenchmarkTable(data.benchmark);
    renderBenchmarkChart(data.benchmark);

    document.getElementById("benchmarkSection").style.display = "block";
    document.getElementById("benchmarkSection").scrollIntoView({ behavior: "smooth", block: "nearest" });
    showToast('<i data-lucide="flag"></i> Benchmark complete!', "success");
  } catch (err) {
    showToast(`<i data-lucide="x-circle"></i> ${err.message}`, "error");
  } finally {
    setLoading(false);
  }
}

// ── Reset ─────────────────────────────────────────────────────────────────
function resetDashboard() {
  ["valMatches","valRate","valTime","valDist"].forEach(id => {
    document.getElementById(id).textContent = "—";
  });
  document.getElementById("mapContainer").style.display  = "none";
  document.getElementById("mapEmpty").style.display   = "flex";
  if (lmap && mapLayerGroup) mapLayerGroup.clearLayers();
  document.getElementById("tripSection").style.display = "none";
  document.getElementById("benchmarkSection").style.display = "none";
  document.getElementById("algoInfo").innerHTML = `<div class="algo-placeholder">Select an algorithm and run a simulation to see complexity analysis.</div>`;
  if (distChart)  { distChart.destroy();  distChart  = null; }
  if (benchChart) { benchChart.destroy(); benchChart = null; }
  lastResult = null;
  showToast('<i data-lucide="rotate-ccw"></i> Dashboard reset', "");
}

// ── Render: Stats ─────────────────────────────────────────────────────────
function renderStats(m) {
  animateNumber("valMatches", m.total_matches, "");
  animateNumber("valRate",    m.match_rate_pct, "%");
  animateNumber("valTime",    m.execution_time_ms, " ms", 2);
  animateNumber("valDist",    m.average_distance, " km", 3);
}

function animateNumber(id, target, suffix = "", decimals = 0) {
  const el    = document.getElementById(id);
  const start = 0;
  const dur   = 700;
  const t0    = performance.now();
  const step  = (now) => {
    const p   = Math.min((now - t0) / dur, 1);
    const val = start + (target - start) * easeOut(p);
    el.textContent = val.toFixed(decimals) + suffix;
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

// ── Render: Algo Info ──────────────────────────────────────────────────────
function renderAlgoInfo(algoKey, metrics) {
  const meta = ALGO_META[algoKey] || {};
  document.getElementById("algoInfo").innerHTML = `
    <div class="algo-block">
      <div class="algo-block-name">${meta.name || algoKey}</div>
      <div class="algo-row"><span class="algo-row-label">Time Complexity</span><span class="algo-row-val">${meta.time}</span></div>
      <div class="algo-row"><span class="algo-row-label">Space Complexity</span><span class="algo-row-val">${meta.space}</span></div>
      <div class="algo-row"><span class="algo-row-label">Drivers Available</span><span class="algo-row-val">${metrics.total_drivers}</span></div>
      <div class="algo-row"><span class="algo-row-label">Passengers Waiting</span><span class="algo-row-val">${metrics.total_passengers}</span></div>
      <div class="algo-row"><span class="algo-row-label">Match Rate</span><span class="algo-row-val">${metrics.match_rate_pct}%</span></div>
      <div class="algo-row"><span class="algo-row-label">Min Pickup Distance</span><span class="algo-row-val">${metrics.min_distance} km</span></div>
      <div class="algo-row"><span class="algo-row-label">Max Pickup Distance</span><span class="algo-row-val">${metrics.max_distance} km</span></div>
    </div>
  `;
}

// ── Render: Map ────────────────────────────────────────────────────────────
function renderMap(drivers, passengers, trips) {
  const container = document.getElementById("mapContainer");
  const empty     = document.getElementById("mapEmpty");
  container.style.display = "block";
  empty.style.display     = "none";

  if (!lmap) {
    lmap = L.map('mapContainer', { zoomControl: false }).setView([20, 78], 5);
    L.control.zoom({ position: 'bottomright' }).addTo(lmap);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(lmap);
    mapLayerGroup = L.layerGroup().addTo(lmap);

    // Recompute sizes on next frame since container just became visible
    setTimeout(() => lmap.invalidateSize(), 50);
  } else {
    mapLayerGroup.clearLayers();
  }

  const bounds = [];
  const matchedDriverIds    = new Set(trips.map(t => t.driver_id));
  const matchedPassengerIds = new Set(trips.map(t => t.passenger_id));

  // Draw Polylines & Tooltips
  trips.forEach(t => {
    const d = drivers.find(x => x.id === t.driver_id);
    const p = passengers.find(x => x.id === t.passenger_id);
    if (d && p) {
      const latlngs = [[d.latitude, d.longitude], [p.pickup_lat, p.pickup_lon]];
      const polyline = L.polyline(latlngs, {
        color: '#10b981', weight: 2, dashArray: '5, 6', opacity: 0.65
      }).addTo(mapLayerGroup);
      bounds.push(latlngs[0], latlngs[1]);

      // Add distance tooltip at the center of the line
      polyline.bindTooltip(`${t.pickup_distance.toFixed(2)} km`, {
        permanent: true, direction: 'center', className: 'leaflet-tooltip'
      });
    }
  });

  // Drivers
  const driverIconBase = L.divIcon({ className: 'marker-driver', iconSize: [12, 12] });
  const driverIconMatc = L.divIcon({ className: 'marker-driver', iconSize: [16, 16], html: `<div style="background:#6366f1;width:100%;height:100%;border-radius:50%;box-shadow:0 0 10px #6366f1"></div>`});
  drivers.forEach(d => {
    const matched = matchedDriverIds.has(d.id);
    const m = L.marker([d.latitude, d.longitude], {
      icon: matched ? driverIconMatc : driverIconBase,
      opacity: matched ? 1.0 : 0.6
    }).addTo(mapLayerGroup);
    m.bindPopup(`<b>Driver #${d.id}</b>`);
    bounds.push([d.latitude, d.longitude]);
  });

  // Passengers
  const passIconBase = L.divIcon({ className: 'marker-passenger', iconSize: [12, 12] });
  const passIconMatc = L.divIcon({ className: 'marker-passenger', iconSize: [16, 16], html: `<div style="background:#a78bfa;width:100%;height:100%;border-radius:50%;box-shadow:0 0 10px #a78bfa"></div>`});
  passengers.forEach(p => {
    const matched = matchedPassengerIds.has(p.id);
    const m = L.marker([p.pickup_lat, p.pickup_lon], {
      icon: matched ? passIconMatc : passIconBase,
      opacity: matched ? 1.0 : 0.6
    }).addTo(mapLayerGroup);
    m.bindPopup(`<b>Passenger #${p.id}</b>`);
    bounds.push([p.pickup_lat, p.pickup_lon]);
  });

  // Fit bounds nicely
  if (bounds.length > 0) {
    lmap.fitBounds(L.latLngBounds(bounds), { padding: [50, 50], maxZoom: 15 });
  }
}

// ── Render: Distance Distribution Chart ───────────────────────────────────
function renderDistChart(trips) {
  if (!trips || trips.length === 0) return;

  const distances = trips.map(t => parseFloat(t.pickup_distance.toFixed(3)));
  const sorted    = [...distances].sort((a, b) => a - b);

  const buckets = 8;
  const minD    = sorted[0];
  const maxD    = sorted[sorted.length - 1];
  const step    = (maxD - minD) / buckets || 0.1;
  const labels  = [];
  const counts  = new Array(buckets).fill(0);

  for (let i = 0; i < buckets; i++) {
    labels.push(`${(minD + i * step).toFixed(2)}`);
  }
  distances.forEach(d => {
    const idx = Math.min(Math.floor((d - minD) / step), buckets - 1);
    counts[idx]++;
  });

  const ctx = document.getElementById("distChart").getContext("2d");
  if (distChart) distChart.destroy();

  distChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Trip Count",
        data:  counts,
        backgroundColor: "rgba(99,102,241,0.55)",
        borderColor:     "#6366f1",
        borderWidth:     1,
        borderRadius:    4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0e1221",
          titleColor: "#94a3b8",
          bodyColor:  "#f1f5f9",
          borderColor: "rgba(99,102,241,0.3)",
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          ticks:  { color: "#475569", font: { size: 10, family: "'JetBrains Mono', monospace" } },
          grid:   { color: "rgba(255,255,255,0.04)" },
          title:  { display: true, text: "Pickup Distance (km)", color: "#475569", font: { size: 10 } },
        },
        y: {
          ticks: { color: "#475569", stepSize: 1 },
          grid:  { color: "rgba(255,255,255,0.04)" },
        },
      },
    },
  });
}

// ── Render: Trip List ──────────────────────────────────────────────────────
function renderTripList(trips) {
  const section = document.getElementById("tripSection");
  const list    = document.getElementById("tripList");
  const count   = document.getElementById("tripCount");

  section.style.display = "block";
  count.textContent = `${trips.length} trip${trips.length !== 1 ? "s" : ""}`;
  list.innerHTML = "";

  trips.forEach((t, i) => {
    const item = document.createElement("div");
    item.className = "trip-item";
    item.style.animationDelay = `${i * 30}ms`;
    item.innerHTML = `
      <div class="trip-main">
        <span class="trip-id">#${t.id}</span>
        <span style="color:#6366f1;font-weight:600;">Driver ${t.driver_id}</span>
        <span class="trip-arrow"><i data-lucide="arrow-right" style="width: 14px; height: 14px;"></i></span>
        <span style="color:#a78bfa;font-weight:600;">Passenger ${t.passenger_id}</span>
      </div>
      <div class="trip-meta">${t.pickup_distance.toFixed(3)} km pickup · ${t.trip_distance.toFixed(3)} km trip</div>
    `;
    list.appendChild(item);
  });
  if (window.lucide) lucide.createIcons();
}

// ── Render: Benchmark Table ────────────────────────────────────────────────
function renderBenchmarkTable(results) {
  const tbody      = document.getElementById("benchBody");
  tbody.innerHTML  = "";

  const complexities = {
    "Greedy Nearest Driver":  "O(P × D)",
    "Heap Priority Queue":    "O((D+P) log D)",
    "Dijkstra Graph Routing": "O(P·(V+E) log V)",
  };

  const minTime = Math.min(...results.map(r => r.execution_time_ms));

  results.forEach(m => {
    const isWinner = m.execution_time_ms === minTime;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${m.algorithm}</td>
      <td class="${isWinner ? "bench-winner" : ""}">${m.execution_time_ms.toFixed(3)} ${isWinner ? '<i data-lucide="award" style="width: 14px; height: 14px;"></i>' : ""}</td>
      <td>${m.total_matches} / ${m.total_passengers}</td>
      <td>${m.match_rate_pct}%</td>
      <td>${m.average_distance} km</td>
      <td class="complexity">${complexities[m.algorithm] || "—"}</td>
    `;
    tbody.appendChild(tr);
  });
  if (window.lucide) lucide.createIcons();
}

// ── Render: Benchmark Chart ────────────────────────────────────────────────
function renderBenchmarkChart(results) {
  const ctx    = document.getElementById("benchChart").getContext("2d");
  const labels = results.map(r => r.algorithm);
  const times  = results.map(r => r.execution_time_ms);
  const colors = ["rgba(99,102,241,0.7)", "rgba(34,211,238,0.7)", "rgba(167,139,250,0.7)"];
  const border = ["#6366f1", "#22d3ee", "#a78bfa"];

  if (benchChart) benchChart.destroy();

  benchChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Execution Time (ms)",
        data:  times,
        backgroundColor: colors,
        borderColor:     border,
        borderWidth:     2,
        borderRadius:    6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      indexAxis: "y",
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0e1221",
          titleColor: "#94a3b8",
          bodyColor:  "#f1f5f9",
          borderColor: "rgba(99,102,241,0.3)",
          borderWidth: 1,
          callbacks: { label: ctx => ` ${ctx.parsed.x.toFixed(3)} ms` },
        },
      },
      scales: {
        x: {
          ticks: { color: "#475569", font: { family: "'JetBrains Mono', monospace", size: 10 } },
          grid:  { color: "rgba(255,255,255,0.04)" },
          title: { display: true, text: "Execution Time (ms)", color: "#475569", font: { size: 10 } },
        },
        y: {
          ticks: { color: "#94a3b8", font: { size: 11 } },
          grid:  { display: false },
        },
      },
    },
  });
}

// ── Loading State ──────────────────────────────────────────────────────────
function setLoading(state) {
  const bar = document.getElementById("loadingBar");
  const btn = document.getElementById("btnSimulate");
  const bnc = document.getElementById("btnBenchmark");
  bar.classList.toggle("hidden", !state);
  btn.disabled = state;
  bnc.disabled = state;
  if (state) {
    btn.innerHTML = '<span class="btn-icon"><i data-lucide="loader-2" class="spin-icon"></i></span> Running…';
  } else {
    btn.innerHTML = '<span class="btn-icon"><i data-lucide="play"></i></span> Run Simulation';
  }
  if (window.lucide) lucide.createIcons();
}

// ── Toast ──────────────────────────────────────────────────────────────────
let toastTimer = null;
function showToast(msg, type = "") {
  const toast = document.getElementById("toast");
  toast.innerHTML    = `<div style="display:flex; align-items:center; gap:0.6rem;">${msg}</div>`;
  toast.className    = `toast flex-toast ${type} show`;
  if (window.lucide) lucide.createIcons();
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3500);
}
