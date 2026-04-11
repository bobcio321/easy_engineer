# 🏎️ Assetto Corsa Race Engineer (Web Panel)

A simple companion tool for Assetto Corsa that allows a second person to act as a **race engineer** through a web browser.

It provides real-time access to car data such as tire conditions, fuel levels, and race status, enabling better communication and strategy during races.

Simply open app on pc and then paste code and password on this site: http://85.184.250.25:3000/

---

## ✨ Features

- 📊 Live telemetry data (tires, fuel, speed, etc.)
- 🌐 Web-based interface (accessible from any device)
- 👨‍🔧 Second person can monitor the race in real time
- ⚡ Lightweight and easy to run
- 🔄 **NEW: Bidirectional pit stop synchronization**
  - Engineer sends pit strategy → Driver receives it
  - Driver sends pit updates → Engineer sees them in real-time
  - Both sides stay synchronized automatically

---

## 🎯 Goal

The goal of this project is to enhance the racing experience by introducing a **team-based dynamic**, where one player drives and another supports them with data and strategy.

---

## 🚀 Quick Start

### For Driver/Application

1. Include `driver.js` in your application
2. Create a new `DriverClient` instance
3. Connect and start sending telemetry
4. Receive pit stop updates from the engineer

```javascript
// Initialize driver client
const driver = new DriverClient('CODE', 'PASS');

// Connect
driver.connect();

// Send telemetry
driver.sendTelemetry({ speed: 200, fuel: 50, ... });

// Send pit stop update
driver.sendPitStop(50, 'Soft', true, false, false);

// Receive updates from engineer
driver.onPitUpdate = (data) => {
  console.log('Engineer strategy:', data);
};
```

**See [DRIVER_GUIDE.md](./DRIVER_GUIDE.md) for detailed documentation**

### For Engineer

1. Run the server
2. Provide driver with session code & password
3. Open web panel and enter credentials
4. Monitor telemetry and send pit strategy
5. See real-time pit updates from driver

---

## 🚧 Status

✅ Working:
- car speed
- gears
- tire temperatures
- tire wear and damage
- fuel level
- **pit stop synchronization in-game via web panel** ✨ NEW
- **driver can send pit stop updates from game** ✨ NEW

🚀 Planned:
- further improvements to telemetry and driver ↔ engineer interaction

---

## 📡 Architecture

### Two-Way Pit Stop Synchronization

```
┌──────────────────────────────────────────────────────┐
│              Easy Engineer System                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  DRIVER/GAME              SERVER         WEB PANEL   │
│  ┌────────────┐         ┌────────┐     ┌─────────┐ │
│  │ driver.js  │ ←────→  │ wsHandler│ ←─┤ dashboard│ │
│  │            │         │        │   │          │ │
│  └────────────┘         └────────┘   └─────────┘ │
│       ▲                       ▲           ▲        │
│       │                       │           │        │
│       └──pit:driver-update────┴───────────┘        │
│                                                      │
│  Telemetry: Driver → Server → Engineers            │
│  Pit Stops: Bidirectional (both ways)              │
└──────────────────────────────────────────────────────┘
```

### Message Types

- `telemetry` - Driver sends car data
- `pit:update` - Engineer/Driver sends pit strategy
- `pit:strategy` - Server broadcasts to engineers
- `pit:driver-update` - Server broadcasts driver pit updates

---

## 📖 How It Works

### Setup
1. **Driver connects** from game/app using `DriverClient`
2. **Server generates** session code and password
3. **Engineer connects** using web panel with code/password
4. **Synchronization begins** automatically

### Pit Stop Strategy Flow
```
Engineer adjusts pit strategy on web panel
           ↓
     Server receives
           ↓
  Broadcasts to Driver
           ↓
Driver sees updated strategy in game
           ↓
Driver decides on pit stop
           ↓
Driver sends pit:update from game
           ↓
     Server receives
           ↓
  Broadcasts to Engineer (with pit:driver-update type)
           ↓
Engineer sees "Driver updated!" notification
```

---

## 🧪 Testing

### Use the Driver Simulator

Open `http://yourserver:3000/driver-simulator.html` to test:
- Connect to server
- Send mock telemetry data
- Receive pit strategy updates
- Send pit stop updates
- See real-time synchronization on web panel

---

## 📚 Files

### Frontend (Client)
- `public/index.html` - Login page
- `public/dashboard.html` - Engineer dashboard
- `public/driver-simulator.html` - Driver test simulator ✨ NEW
- `public/js/login.js` - Login logic
- `public/js/dashboard.js` - Dashboard logic (updated with pit:driver-update)
- `public/js/driver.js` - DriverClient for apps/games ✨ NEW
- `public/css/style.css` - Styling

### Backend (Server)
- `server/server.js` - Express + WebSocket server
- `server/wsHandler.js` - WebSocket message handlers (updated for bidirectional pit)
- `server/sessionManager.js` - Session management

### Documentation
- `README.md` - This file
- `DRIVER_GUIDE.md` - Driver implementation guide ✨ NEW

---

## 🔧 Installation & Running

```bash
# Install dependencies
cd server
npm install

# Run server
npm start
# Server runs on http://0.0.0.0:3000

# Or with environment variables
HOST=127.0.0.1 PORT=3000 npm start
```

Then open in browser: `http://localhost:3000/`

---

## 💡 Example: Using Driver Client

```javascript
// Initialize
const driver = new DriverClient('ABC123', '1234');

// Set up callbacks
driver.onConnected = () => console.log('Connected!');
driver.onPitUpdate = (data) => {
  console.log('Pit strategy:', data);
  applyPitStrategyToGame(data);
};

// Connect
driver.connect();

// Send telemetry regularly (every 50-100ms)
setInterval(() => {
  driver.sendTelemetry({
    speed: gameData.speed,
    gear: gameData.gear,
    fuel: gameData.fuel,
    maxFuel: gameData.maxFuel,
    lap: gameData.lap,
    lastLap: gameData.lastLapTime,
    bestLap: gameData.bestLapTime,
    tireTemp: [gameData.tireTempFL, gameData.tireTempFR, ...],
    tireWear: [gameData.tireWearFL, gameData.tireWearFR, ...],
    // ... more fields
  });
}, 100);

// When driver decides on pit stop
function doPitStop() {
  driver.sendPitStop(
    fuel = 50,           // liters
    compound = 'Soft',
    changeTires = true,
    repairBody = false,
    repairEngine = false
  );
}
```

---

## 🔌 API Reference

### DriverClient

```javascript
// Constructor
new DriverClient(sessionCode, password)

// Methods
connect()                    // Connect to server
disconnect()                 // Disconnect from server
sendTelemetry(data)         // Send telemetry data
sendPitUpdate(pitData)      // Send pit stop update
sendPitStop(...)            // Send pit stop with parameters

// Callbacks
onConnected()               // When connected
onDisconnected()            // When disconnected
onSessionCreated(code, password)  // On session creation
onPitUpdate(data)           // When engineer sends pit strategy
onError(error)              // On error
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Driver not connecting | Check server is running, firewall rules, URL is correct |
| Engineer doesn't see driver | Driver must connect before engineer joins |
| Pit updates not syncing | Check browser console for errors, verify WebSocket connection |
| Telemetry not updating | Send data more frequently, check data format |

---

## 📝 Development Notes

- WebSocket for real-time communication
- Session-based authentication with code/password
- In-memory session storage (resets on server restart)
- Automatic reconnection for clients

---

## 🎓 Use Cases

1. **Online Racing Championships** - Remote engineer support
2. **Gaming Tournaments** - Multiple team members controlling strategy
3. **Simulator Training** - Coach monitoring performance
4. **Team Racing** - Coordinated pit stop strategy
5. **Game Development** - Test telemetry systems

---

## 📄 License

This project is open source.

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

