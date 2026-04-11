# Easy Engineer - Driver Implementation Guide

## Przegląd

Kierowca/aplikacja gry może teraz wysyłać i odbierać dane pit stop'u w real-time. System automatycznie synchronizuje zmiany między kierowcą a inżynierem na web panelu.

## Instalacja

### 1. Dołącz skrypt driver.js do aplikacji:

```html
<script src="path/to/driver.js"></script>
```

## Wykorzystanie

### Inicjalizacja

Ów skrypt został stworzony z myślą, aby mógł być użyty zarówno w aplikacji gry jak i w testach:

```javascript
const driverClient = new DriverClient('ABC123', 'PASS');

// Ustaw callback dla sesji
driverClient.onSessionCreated = (code, password) => {
  console.log(`Session code: ${code}`);
  console.log(`Session password: ${password}`);
  // Wyślij te dane do inżyniera - może to zrobić poprzez SMS, email, itp.
};

// Ustaw callback dla aktualizacji pit stop'u z panelu web
driverClient.onPitUpdate = (pitData) => {
  console.log('Pit strategy updated by engineer:', pitData);
  // Zastosuj strategię pit stop'u w grze
  applyPitStrategy(pitData);
};

// Ustaw callback dla błędów
driverClient.onError = (error) => {
  console.error('Error:', error);
};

// Połącz się z serwerem
driverClient.connect();
```

### Wysyłanie telemetrii

```javascript
// Wysyłaj telemetrię z gry w regularnych interwałach (np. co 10-100ms):
setInterval(() => {
  const telemetry = {
    speed: 200,         // km/h
    gear: 5,            // 0=R, 1=N, 2+=forward
    fuel: 45.5,         // liters
    maxFuel: 120,       // liters
    lap: 5,             // current lap
    lastLap: 125000,    // ms
    bestLap: 120000,    // ms
    fuelPerLap: 2.5,    // liters per lap

    // Tire data
    tireTemp: [80, 82, 78, 79],    // [FL, FR, RL, RR] °C
    tireWear: [75, 70, 80, 72],    // [FL, FR, RL, RR] %
    tirePressure: [27.5, 27.4, 28.1, 28.0], // [FL, FR, RL, RR] psi
    brakeTemp: [450, 460, 440, 450], // [FL, FR, RL, RR] °C

    // Car info
    carModel: 'Ferrari 488 GT3',
    track: 'Monza',
    trackConfig: 'GP',
    position: 1,
    numberOfLaps: 30,

    // Damage
    carDamage: [0, 5, 0, 2],       // [front, rear, left, right] %

    // Environment
    airTemp: 25,        // °C
    roadTemp: 35,       // °C
    tyreCompound: 'Soft'
  };

  driverClient.sendTelemetry(telemetry);
}, 50); // Wyślij co 50ms
```

### Wysyłanie aktualizacji pit stop'u

Gdy kierowca decyduje o pit stop'ie lub zmienia strategię:

```javascript
// Metoda 1: Wysłanie pełnych danych pit stop'u
driverClient.sendPitStop(
  fuel = 50,           // liters to add
  tireCompound = 'Soft',
  changeTires = true,
  repairBody = false,
  repairEngine = false
);

// Metoda 2: Wysłanie obiektu danych
const pitStrategy = {
  fuel: 50,
  tireCompound: 'Hard',
  changeTires: true,
  repairBody: true,  // Jeśli jest uszkodzenie
  repairEngine: false
};

driverClient.sendPitUpdate(pitStrategy);
```

### Odbieranie aktualizacji od inżyniera

```javascript
driverClient.onPitUpdate = (pitData) => {
  console.log('Pit strategy from engineer:');
  console.log('- Fuel:', pitData.fuel, 'L');
  console.log('- Tire compound:', pitData.tireCompound);
  console.log('- Change tires:', pitData.changeTires);
  console.log('- Repair body:', pitData.repairBody);
  console.log('- Repair engine:', pitData.repairEngine);

  // Tutaj możesz zastosować strategię do gry lub wyświetlić ostrzeżenie dla gracza
};
```

## Pełny Przykład Implementacji

```javascript
// Inicjalizacja
const driverClient = new DriverClient('ABC123', '1234');

// Callbacki
driverClient.onSessionCreated = (code, password) => {
  document.getElementById('sessionInfo').textContent =
    `Connect with: Code: ${code}, Password: ${password}`;
};

driverClient.onConnected = () => {
  document.getElementById('status').textContent = 'Connected ✓';
  document.getElementById('status').className = 'connected';
};

driverClient.onDisconnected = () => {
  document.getElementById('status').textContent = 'Disconnected';
  document.getElementById('status').className = 'disconnected';
};

driverClient.onPitUpdate = (pitData) => {
  document.getElementById('pitInfo').innerHTML = `
    <h3>Pit Stop Strategy</h3>
    <p>Fuel: ${pitData.fuel} L</p>
    <p>Tires: ${pitData.tireCompound}</p>
    <p>Change tires: ${pitData.changeTires ? 'Yes' : 'No'}</p>
  `;
};

driverClient.onError = (error) => {
  console.error('Client error:', error);
};

// Połączenie
driverClient.connect();

// Symulacja telemetrii
setInterval(() => {
  driverClient.sendTelemetry({
    speed: 200 + Math.random() * 50,
    gear: 5,
    fuel: 45 - Math.random() * 2,
    maxFuel: 120,
    lap: 5,
    lastLap: 125000,
    bestLap: 120000,
    fuelPerLap: 2.5,
    tireTemp: [85, 87, 83, 84],
    tireWear: [75, 70, 80, 72],
    carModel: 'Ferrari 488 GT3',
    track: 'Monza'
  });
}, 100);

// Przycisk do wysyłania pit stop'u
document.getElementById('pitBtn').addEventListener('click', () => {
  driverClient.sendPitStop(50, 'Soft', true, false, false);
});

// Zamknięcie
window.addEventListener('beforeunload', () => {
  driverClient.disconnect();
});
```

## Schemat Przepływu Danych

```
┌─────────────────────────────────────────────────────────────────┐
│                    Easy Engineer System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  KIEROWCA/APLIKACJA GRY          SERVER          WEB PANEL      │
│  ┌──────────────┐             ┌─────────┐      ┌────────────┐  │
│  │ driverClient │←────────────→│ wsHandler│←────┤ dashboard  │  │
│  │              │              │         │     │            │  │
│  │ - Telemetry  │ sendTelemetry│         │     │ - Monitor  │  │
│  │ - Pit updates│              │         │     │ - Send pit  │  │
│  │ - Receive    │ pit:update   │         │     │   strategy │  │
│  │   updates    │              │         │     │ - View      │  │
│  └──────────────┘              └─────────┘     │   changes  │  │
│         ▲                           │           └────────────┘  │
│         │                           │                           │
│         └───────pit:driver-update───┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Przepływ:
1. Kierowca wysyła telemetrię (co ~100ms)
2. Server rozsyła telemetrię do inżyniera
3. Inżynier wysyła pit strategy z panelu web
4. Server wysyła pit:update do kierowcy
5. Kierowca wysyła pit:update ze swojej aplikacji
6. Server wysyła pit:driver-update do inżyniera
7. Inżynier widzi aktualizację ze źródła kierowcy
```

## Obsługiwane Pola Telemetrii

```javascript
{
  // Prędkość i jazda
  speed: Number,           // km/h
  gear: Number,            // 0=R, 1=N, 2-7=forward gears

  // Paliwo
  fuel: Number,            // liters
  maxFuel: Number,         // liters
  fuelPerLap: Number,      // liters per lap

  // Okrążenia
  lap: Number,             // current lap
  lastLap: Number,         // ms
  bestLap: Number,         // ms

  // Opony
  tireTemp: [Number, Number, Number, Number],     // [FL, FR, RL, RR] °C
  tireWear: [Number, Number, Number, Number],     // [FL, FR, RL, RR] %
  tirePressure: [Number, Number, Number, Number], // [FL, FR, RL, RR] psi

  // Hamulce
  brakeTemp: [Number, Number, Number, Number],    // [FL, FR, RL, RR] °C

  // Samochód
  carModel: String,        // e.g. "Ferrari 488 GT3"
  carDamage: [Number, Number, Number, Number], // [front, rear, left, right] %

  // Tor
  track: String,           // e.g. "Monza"
  trackConfig: String,     // e.g. "GP"
  position: Number,        // position in race
  numberOfLaps: Number,    // total laps

  // Warunki
  airTemp: Number,         // °C
  roadTemp: Number,        // °C
  tyreCompound: String     // "Soft", "Medium", "Hard", "Wet"
}
```

## API DriverClient

### Właściwości

- `connected`: boolean - Status połączenia
- `sessionCode`: string - Kod sesji
- `password`: string - Hasło sesji

### Metody

- `connect()` - Połącz się z serwerem
- `disconnect()` - Rozłącz się z serwerem
- `sendTelemetry(data)` - Wyślij dane telemetrii
- `sendPitUpdate(pitData)` - Wyślij aktualizację pit stop'u
- `sendPitStop(fuel, compound, changeTires, repairBody, repairEngine)` - Wyślij pit stop

### Callbacki

- `onConnected()` - Gdy połączenie zostało nawiązane
- `onDisconnected()` - Gdy połączenie zostało zerwane
- `onSessionCreated(code, password)` - Gdy sesja została utworzona
- `onPitUpdate(data)` - Gdy inżynier wysłał aktualizację pit stop'u
- `onError(error)` - Gdy произошла ошибka

## Notatki

- Telemetrię należy wysyłać regularnie (co ~100ms) dla płynnych aktualizacji
- Pit stop data jest automatycznie synchronizowana między oboma stronami
- Web panel pokazuje "Driver updated!" gdy kierowca wysyła pit stop data
- Wszystkie komunikaty są wysyłane przez WebSockets dla minimalnego opóźnienia
- Połączenie automatycznie się ponawia w przypadku utraty

## Poradnictwo

Jeśli masz problemy:
1. Sprawdź konsolę przeglądarki za błędami
2. Sprawdź czy aplikacja ma dostęp do serwera (firewall)
3. Upewnij się że sesja jest prawidłowa (kod i hasło)
4. Sprawdź czy driver jest podłączony zanim inżynier się połączy
