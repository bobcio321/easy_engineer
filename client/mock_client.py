"""Mock client for testing Easy Engineer without Assetto Corsa.

Generates realistic fake telemetry data and sends it to the server.
"""

import argparse
import asyncio
import json
import math
import random
import time

import websockets


class MockTelemetry:
    def __init__(self):
        self.t = 0
        self.lap = 1
        self.lap_start = time.time()
        self.last_lap_ms = 0
        self.best_lap_ms = 0
        self.fuel = 50.0
        self.fuel_per_lap = 2.8
        self.damage = [0.0, 0.0, 0.0, 0.0, 0.0]  # front, rear, left, right, ?

    def tick(self, dt):
        self.t += dt
        phase = self.t * 0.3

        # Speed: varies between 40-280 km/h with some pattern
        speed = 160 + 120 * math.sin(phase) + random.uniform(-5, 5)
        speed = max(0, speed)

        # Gear based on speed
        if speed < 60:
            gear = 2
        elif speed < 100:
            gear = 3
        elif speed < 150:
            gear = 4
        elif speed < 200:
            gear = 5
        else:
            gear = 6

        rpm = int(3000 + (speed / 280) * 5000 + random.uniform(-200, 200))

        # Tire temps: vary around 80-105°C
        base_temp = 85 + 15 * math.sin(phase * 0.5)
        tire_temp = [
            round(base_temp + random.uniform(-3, 3), 1),
            round(base_temp + random.uniform(-3, 5), 1),
            round(base_temp - 2 + random.uniform(-3, 3), 1),
            round(base_temp - 2 + random.uniform(-3, 5), 1),
        ]

        # Tire wear: slowly decreasing
        base_wear = max(0, 100 - self.t * 0.15)
        tire_wear = [
            round(base_wear + random.uniform(-2, 0), 1),
            round(base_wear + random.uniform(-3, 0), 1),
            round(base_wear + random.uniform(-1, 0), 1),
            round(base_wear + random.uniform(-2, 0), 1),
        ]

        # Tire pressure: ~26-28 psi
        tire_pressure = [
            round(27.0 + random.uniform(-1, 1), 1),
            round(27.0 + random.uniform(-1, 1), 1),
            round(26.5 + random.uniform(-1, 1), 1),
            round(26.5 + random.uniform(-1, 1), 1),
        ]

        # Brake temps: 200-600°C depending on braking
        brake_base = 350 + 150 * math.sin(phase * 1.5)
        brake_temp = [
            round(brake_base + random.uniform(-30, 30), 1),
            round(brake_base + random.uniform(-30, 30), 1),
            round(brake_base - 20 + random.uniform(-30, 30), 1),
            round(brake_base - 20 + random.uniform(-30, 30), 1),
        ]

        # Simulate occasional damage accumulation
        if random.random() < 0.002:  # rare contact
            zone = random.randint(0, 3)
            self.damage[zone] = min(100, self.damage[zone] + random.uniform(5, 25))

        # Fuel: decreasing
        self.fuel -= self.fuel_per_lap * dt / 90  # ~90s per lap
        self.fuel = max(0, self.fuel)

        # Lap timing ~85-95s per lap
        elapsed = time.time() - self.lap_start
        current_lap_ms = int(elapsed * 1000)

        if elapsed > 85 + random.uniform(0, 10):
            self.last_lap_ms = current_lap_ms
            if self.best_lap_ms == 0 or current_lap_ms < self.best_lap_ms:
                self.best_lap_ms = current_lap_ms
            self.lap += 1
            self.lap_start = time.time()
            current_lap_ms = 0

        return {
            "speed": round(speed, 1),
            "fuel": round(self.fuel, 2),
            "gear": gear,
            "rpm": rpm,
            "maxRpm": 8500,
            "maxFuel": 60.0,
            "tireTemp": tire_temp,
            "tireWear": tire_wear,
            "tirePressure": tire_pressure,
            "brakeTemp": brake_temp,
            "lap": self.lap,
            "lastLap": self.last_lap_ms,
            "bestLap": self.best_lap_ms,
            "currentLap": current_lap_ms,
            "fuelPerLap": self.fuel_per_lap,
            "carModel": "Mock Car GT3",
            "carSkin": "red_white_1",
            "track": "Mock Circuit",
            "trackConfig": "GP Layout",
            "tyreCompound": "Medium",
            "carDamage": [round(d, 2) for d in self.damage],
            "abs": 0.0,
            "tc": 0.0,
            "drs": 0,
            "pitLimiter": 0,
            "isInPit": 0,
            "isInPitLane": 0,
            "position": 1,
            "numberOfLaps": 30,
            "sessionTimeLeft": max(0, 2700 - self.t),
            "airTemp": 24.5,
            "roadTemp": 32.1,
            "maxPower": 430.0,
            "maxTorque": 520.0,
            "hasDRS": 0,
            "hasERS": 0,
            "hasKERS": 0,
            "aidMechanicalDamage": 100.0,
            "rainTyres": 0,
        }


async def run(server_url, interval):
    while True:
        try:
            print(f"[*] Connecting to {server_url}...")
            async with websockets.connect(server_url) as ws:
                print("[*] Connected!")

                mock = MockTelemetry()
                session_info = None

                async def receive():
                    nonlocal session_info
                    async for raw in ws:
                        msg = json.loads(raw)
                        if msg["type"] == "session:created":
                            session_info = msg
                            print()
                            print("=" * 40)
                            print("  MOCK SESSION CREATED")
                            print(f"  Code:     {msg['code']}")
                            print(f"  Password: {msg['password']}")
                            print("=" * 40)
                            print()
                        elif msg["type"] == "pit:update":
                            data = msg["data"]
                            print()
                            print(">>> PIT STRATEGY UPDATE <<<")
                            print(f"  Fuel:         {data.get('fuel', 0)} L")
                            print(f"  Compound:     {data.get('tireCompound', 'N/A')}")
                            print(f"  Change tires: {'Yes' if data.get('changeTires') else 'No'}")
                            print(f"  Repair body:  {'Yes' if data.get('repairBody') else 'No'}")
                            print(f"  Repair engine:{'Yes' if data.get('repairEngine') else 'No'}")
                            print()

                async def send():
                    while True:
                        data = mock.tick(interval)
                        await ws.send(json.dumps({"type": "telemetry", "data": data}))
                        await asyncio.sleep(interval)

                recv_task = asyncio.create_task(receive())
                send_task = asyncio.create_task(send())
                done, pending = await asyncio.wait(
                    [recv_task, send_task], return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()

        except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            print(f"[!] Connection error: {e}. Retrying in 3s...")
            await asyncio.sleep(3)


def main():
    parser = argparse.ArgumentParser(description="Easy Engineer Mock Client")
    parser.add_argument(
        "--server",
        default="ws://localhost:3000/ws/driver",
        help="Server WebSocket URL",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.2,
        help="Send interval in seconds (default: 0.2)",
    )
    args = parser.parse_args()

    print("Easy Engineer — Mock Telemetry Client")
    print("Press Ctrl+C to stop\n")

    try:
        asyncio.run(run(args.server, args.interval))
    except KeyboardInterrupt:
        print("\n[*] Stopped.")


if __name__ == "__main__":
    main()
