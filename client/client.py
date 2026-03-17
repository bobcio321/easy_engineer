"""Easy Engineer — Assetto Corsa telemetry client.

Reads AC shared memory and sends telemetry to the Easy Engineer server.
Receives pit stop commands from the engineer.
"""

import argparse
import asyncio
import json
import sys
import time

import websockets

from ac_shared_memory import ACTelemetry


class EasyEngineerClient:
    def __init__(self, server_url, interval=0.2):
        self.server_url = server_url
        self.interval = interval
        self.telemetry = ACTelemetry()
        self.ws = None
        self.session_code = None
        self.session_password = None
        self.pit_strategy = None
        self.last_fuel = None
        self.last_lap = None
        self.fuel_per_lap = 0

    async def run(self):
        while True:
            try:
                await self.connect()
            except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                print(f"[!] Connection lost: {e}. Reconnecting in 3s...")
                await asyncio.sleep(3)

    async def connect(self):
        print(f"[*] Connecting to {self.server_url}...")
        async with websockets.connect(self.server_url) as ws:
            self.ws = ws
            print("[*] Connected! Waiting for session...")

            recv_task = asyncio.create_task(self.receive_loop())
            send_task = asyncio.create_task(self.send_loop())

            done, pending = await asyncio.wait(
                [recv_task, send_task], return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()

    async def receive_loop(self):
        async for raw in self.ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg["type"] == "session:created":
                self.session_code = msg["code"]
                self.session_password = msg["password"]
                print()
                print("=" * 40)
                print("  SESSION CREATED")
                print(f"  Code:     {self.session_code}")
                print(f"  Password: {self.session_password}")
                print("=" * 40)
                print()
                print("[*] Share these with your engineer.")
                print("[*] Waiting for AC telemetry...")
                print()

            elif msg["type"] == "pit:update":
                self.pit_strategy = msg["data"]
                print()
                print(">>> PIT STRATEGY UPDATE <<<")
                print(f"  Fuel:         {self.pit_strategy.get('fuel', 0)} L")
                print(f"  Compound:     {self.pit_strategy.get('tireCompound', 'N/A')}")
                print(f"  Change tires: {'Yes' if self.pit_strategy.get('changeTires') else 'No'}")
                print(f"  Repair body:  {'Yes' if self.pit_strategy.get('repairBody') else 'No'}")
                print(f"  Repair engine:{'Yes' if self.pit_strategy.get('repairEngine') else 'No'}")
                print()

    async def send_loop(self):
        ac_connected = False

        while True:
            if not ac_connected:
                if self.telemetry.connect():
                    ac_connected = True
                    print("[*] AC shared memory connected!")
                else:
                    await asyncio.sleep(1)
                    continue

            data = self.telemetry.read()
            if data is None:
                ac_connected = False
                self.telemetry.disconnect()
                print("[!] Lost AC connection, retrying...")
                await asyncio.sleep(1)
                continue

            # Fuel per lap: prefer AC's value, fall back to manual calc
            current_lap = data.get("lap", 0)
            current_fuel = data.get("fuel", 0)

            if self.last_lap is not None and current_lap > self.last_lap:
                fuel_used = self.last_fuel - current_fuel
                if fuel_used > 0:
                    self.fuel_per_lap = round(fuel_used, 2)
                self.last_fuel = current_fuel

            if self.last_lap is None or current_lap > self.last_lap:
                self.last_lap = current_lap
                if self.last_fuel is None:
                    self.last_fuel = current_fuel

            ac_fpl = data.get("fuelPerLap", 0)
            data["fuelPerLap"] = ac_fpl if ac_fpl > 0 else self.fuel_per_lap

            await self.ws.send(json.dumps({"type": "telemetry", "data": data}))
            await asyncio.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser(description="Easy Engineer AC Client")
    parser.add_argument(
        "--server",
        default="ws://localhost:3000/ws/driver",
        help="Server WebSocket URL (default: ws://localhost:3000/ws/driver)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.2,
        help="Telemetry send interval in seconds (default: 0.2 = 5Hz)",
    )
    args = parser.parse_args()

    client = EasyEngineerClient(args.server, args.interval)

    print("Easy Engineer — AC Telemetry Client")
    print("Press Ctrl+C to stop\n")

    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        client.telemetry.disconnect()


if __name__ == "__main__":
    main()
