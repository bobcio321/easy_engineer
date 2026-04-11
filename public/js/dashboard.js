const code = sessionStorage.getItem('ee_code');
const password = sessionStorage.getItem('ee_password');

if (!code || !password) {
  window.location.href = '/';
}

// DOM elements
const connStatus = document.getElementById('connStatus');
const speedEl = document.getElementById('speed');
const gearEl = document.getElementById('gear');
const fuelEl = document.getElementById('fuel');
const fuelBar = document.getElementById('fuelBar');
const fuelPerLapEl = document.getElementById('fuelPerLap');
const fuelLapsLeftEl = document.getElementById('fuelLapsLeft');
const lapNumberEl = document.getElementById('lapNumber');
const lastLapEl = document.getElementById('lastLap');
const bestLapEl = document.getElementById('bestLap');
const lapHistoryEl = document.getElementById('lapHistory');
const sessionOverlay = document.getElementById('sessionOverlay');

// New DOM elements
const carInfoEl = document.getElementById('carInfo');
const trackNameEl = document.getElementById('trackName');
const tyreCompoundEl = document.getElementById('tyreCompound');
const posInfoEl = document.getElementById('posInfo');
const airTempEl = document.getElementById('airTemp');
const roadTempEl = document.getElementById('roadTemp');

// Damage elements
const dmgFront = document.getElementById('dmgFront');
const dmgRear = document.getElementById('dmgRear');
const dmgLeft = document.getElementById('dmgLeft');
const dmgRight = document.getElementById('dmgRight');
const dmgFrontVal = document.getElementById('dmgFrontVal');
const dmgRearVal = document.getElementById('dmgRearVal');
const dmgLeftVal = document.getElementById('dmgLeftVal');
const dmgRightVal = document.getElementById('dmgRightVal');

// Pit controls
const pitFuel = document.getElementById('pitFuel');
const pitCompound = document.getElementById('pitCompound');
const pitChangeTires = document.getElementById('pitChangeTires');
const pitRepairBody = document.getElementById('pitRepairBody');
const pitRepairEngine = document.getElementById('pitRepairEngine');
const pitSendBtn = document.getElementById('pitSendBtn');
const pitFlash = document.getElementById('pitFlash');

// Tire elements
const tireIds = ['fl', 'fr', 'rl', 'rr'];

let ws = null;
let lapHistory = [];
let lastLapNumber = 0;

function formatLapTime(ms) {
  if (!ms || ms <= 0) return '-:--.---';
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = Math.floor(ms % 1000);
  return `${minutes}:${String(seconds).padStart(2, '0')}.${String(millis).padStart(3, '0')}`;
}

function getTempClass(temp) {
  if (temp < 70) return 'temp-cold';
  if (temp < 100) return 'temp-good';
  if (temp < 110) return 'temp-warm';
  return 'temp-hot';
}

function getBrakeTempClass(temp) {
  if (temp < 200) return 'temp-cold';
  if (temp < 400) return 'temp-good';
  if (temp < 600) return 'temp-warm';
  return 'temp-hot';
}

function getWearClass(wear) {
  if (wear > 50) return 'wear-good';
  if (wear > 25) return 'wear-mid';
  return 'wear-low';
}

function getDamageClass(dmg) {
  if (dmg < 5) return 'dmg-none';
  if (dmg < 30) return 'dmg-light';
  if (dmg < 60) return 'dmg-medium';
  return 'dmg-heavy';
}

function getCompoundClass(compound) {
  const c = (compound || '').toLowerCase();
  if (c.includes('soft')) return 'compound-soft';
  if (c.includes('hard')) return 'compound-hard';
  if (c.includes('wet') || c.includes('rain')) return 'compound-wet';
  return 'compound-medium';
}

function updateTelemetry(data) {
  // Speed & gear
  speedEl.textContent = Math.round(data.speed || 0);
  gearEl.textContent = data.gear === 0 ? 'R' : data.gear === 1 ? 'N' : data.gear - 1;

  // Car info & track
  if (data.carModel) carInfoEl.textContent = data.carModel;
  if (data.track) {
    let trackText = data.track;
    if (data.trackConfig) trackText += ` — ${data.trackConfig}`;
    trackNameEl.textContent = trackText;
  }

  // Tyre compound
  if (data.tyreCompound) {
    tyreCompoundEl.textContent = data.tyreCompound;
    tyreCompoundEl.className = `compound-badge ${getCompoundClass(data.tyreCompound)}`;
  }

  // Position
  if (data.position) {
    let posText = `P${data.position}`;
    if (data.numberOfLaps > 0) posText += ` / ${data.numberOfLaps} laps`;
    posInfoEl.textContent = posText;
  }

  // Conditions
  if (data.airTemp != null) airTempEl.textContent = `${data.airTemp}°C`;
  if (data.roadTemp != null) roadTempEl.textContent = `${data.roadTemp}°C`;

  // Tire temps
  const temps = data.tireTemp || [0, 0, 0, 0];
  tireIds.forEach((id, i) => {
    const box = document.getElementById(`tire-${id}`);
    const tempVal = Math.round(temps[i]);
    box.querySelector('.tire-temp').textContent = `${tempVal}°C`;
    box.querySelector('.tire-temp').className = `tire-temp ${getTempClass(temps[i])}`;
  });

  // Tire wear
  const wear = data.tireWear || [100, 100, 100, 100];
  tireIds.forEach((id, i) => {
    const box = document.getElementById(`wear-${id}`);
    const pct = Math.round(wear[i]);
    box.querySelector('.tire-temp').textContent = `${pct}%`;
    const wearClass = getWearClass(pct);
    box.querySelector('.tire-wear-bar').className = `tire-wear-bar ${wearClass}`;
    box.querySelector('.tire-wear-fill').style.width = `${pct}%`;
  });

  // Brake temps
  const brakes = data.brakeTemp || [0, 0, 0, 0];
  tireIds.forEach((id, i) => {
    const box = document.getElementById(`brake-${id}`);
    if (box) {
      const bVal = Math.round(brakes[i]);
      const tempEl = box.querySelector('.brake-temp-val');
      tempEl.textContent = `${bVal}°C`;
      tempEl.className = `tire-temp brake-temp-val ${getBrakeTempClass(brakes[i])}`;
    }
  });

  // Tire pressure
  const pressure = data.tirePressure || [0, 0, 0, 0];
  tireIds.forEach((id, i) => {
    const box = document.getElementById(`press-${id}`);
    if (box) {
      box.querySelector('.tire-temp').textContent = `${pressure[i].toFixed(1)} psi`;
    }
  });

  // Car damage: [front, rear, left, right, ?]
  const dmg = data.carDamage || [0, 0, 0, 0, 0];
  dmgFrontVal.textContent = `${Math.round(dmg[0])}%`;
  dmgRearVal.textContent = `${Math.round(dmg[1])}%`;
  dmgLeftVal.textContent = `${Math.round(dmg[2])}%`;
  dmgRightVal.textContent = `${Math.round(dmg[3])}%`;
  dmgFront.className = `damage-zone damage-front ${getDamageClass(dmg[0])}`;
  dmgRear.className = `damage-zone damage-rear ${getDamageClass(dmg[1])}`;
  dmgLeft.className = `damage-zone damage-left ${getDamageClass(dmg[2])}`;
  dmgRight.className = `damage-zone damage-right ${getDamageClass(dmg[3])}`;

  // Fuel
  const fuel = data.fuel || 0;
  const maxFuel = data.maxFuel || 100;
  const fuelPct = Math.min(100, (fuel / maxFuel) * 100);
  fuelEl.textContent = fuel.toFixed(1);
  fuelBar.style.width = `${fuelPct}%`;

  const fpl = data.fuelPerLap || 0;
  fuelPerLapEl.textContent = fpl > 0 ? fpl.toFixed(2) : '--';
  fuelLapsLeftEl.textContent = fpl > 0 ? Math.floor(fuel / fpl) : '--';

  // Lap info
  lapNumberEl.textContent = data.lap || '-';
  lastLapEl.textContent = formatLapTime(data.lastLap);
  bestLapEl.textContent = formatLapTime(data.bestLap);

  // Lap history tracking
  if (data.lap && data.lap > lastLapNumber && data.lastLap > 0) {
    lapHistory.unshift({
      lap: data.lap - 1,
      time: data.lastLap,
      fuelUsed: fpl > 0 ? fpl.toFixed(2) : '--',
    });
    if (lapHistory.length > 15) lapHistory.pop();
    renderLapHistory();
    lastLapNumber = data.lap;
  } else if (data.lap && lastLapNumber === 0) {
    lastLapNumber = data.lap;
  }
}

function renderLapHistory() {
  lapHistoryEl.innerHTML = lapHistory.map((l) =>
    `<tr><td>${l.lap}</td><td>${formatLapTime(l.time)}</td><td>${l.fuelUsed} L</td></tr>`
  ).join('');
}

function updatePitStrategy(data, fromDriver = false) {
  pitFuel.value = data.fuel || 0;
  pitCompound.value = data.tireCompound || 'Medium';
  pitChangeTires.checked = !!data.changeTires;
  pitRepairBody.checked = !!data.repairBody;
  pitRepairEngine.checked = !!data.repairEngine;

  if (fromDriver) {
    pitFlash.classList.add('visible');
    pitFlash.textContent = 'Driver updated!';
    setTimeout(() => {
      pitFlash.classList.remove('visible');
      pitFlash.textContent = 'Sent!';
    }, 1500);
  }
}

function connect() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${protocol}//${location.host}/ws/engineer`);

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'engineer:join', code, password }));
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    switch (msg.type) {
      case 'auth:ok':
        connStatus.textContent = 'Connected';
        connStatus.className = 'connection-status status-connected';
        break;

      case 'auth:fail':
        sessionStorage.clear();
        window.location.href = '/';
        break;

      case 'telemetry':
        updateTelemetry(msg.data);
        break;

      case 'pit:strategy':
        updatePitStrategy(msg.data, false);
        break;

      case 'pit:driver-update':
        updatePitStrategy(msg.data, true);
        break;

      case 'session:ended':
        sessionOverlay.classList.remove('hidden');
        break;
    }
  };

  ws.onclose = () => {
    connStatus.textContent = 'Disconnected';
    connStatus.className = 'connection-status status-disconnected';
    setTimeout(connect, 2000);
  };

  ws.onerror = () => {
    ws.close();
  };
}

// Send pit strategy
pitSendBtn.addEventListener('click', () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  const data = {
    fuel: Number(pitFuel.value) || 0,
    tireCompound: pitCompound.value,
    changeTires: pitChangeTires.checked,
    repairBody: pitRepairBody.checked,
    repairEngine: pitRepairEngine.checked,
  };

  ws.send(JSON.stringify({ type: 'pit:update', data }));

  pitFlash.classList.add('visible');
  setTimeout(() => pitFlash.classList.remove('visible'), 1500);
});

connect();
