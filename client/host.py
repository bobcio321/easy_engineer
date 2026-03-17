"""Easy Engineer — Host GUI Application.

Desktop GUI for the driver to configure server connection, view session credentials,
preview telemetry, and receive pit strategy updates from the engineer.

Usage:
    python host.py              # Normal mode (reads AC shared memory)
    python host.py --mock       # Mock mode (fake telemetry for testing)
    python host.py --server ws://example.com:3000/ws/driver
"""

import argparse
import asyncio
import json
import threading
import time
import tkinter as tk
from datetime import datetime

import websockets

from ac_shared_memory import ACTelemetry
from mock_client import MockTelemetry

# Dark theme colors (matching web dashboard)
BG = "#0d1117"
BG_CARD = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
YELLOW = "#d29922"
RED = "#f85149"


class HostApp:
    def __init__(self, mock=False):
        self.mock = mock

        # Async state
        self._loop = None
        self._thread = None
        self._ws = None
        self._running = False
        self._connect_task = None

        # Telemetry
        self._ac = None
        self._mock_telemetry = None
        self._last_fuel = None
        self._last_lap = None
        self._fuel_per_lap = 0

        # Build GUI
        self.root = tk.Tk()
        self.root.title("Easy Engineer — Host")
        self.root.geometry("520x880")
        self.root.resizable(False, True)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._set_status("Disconnected", RED)

    # ── UI construction ──────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(12, 0))
        tk.Label(hdr, text="Easy Engineer", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text="v1.0", font=("Segoe UI", 10),
                 bg=BG, fg=TEXT_DIM).pack(side="right", pady=(8, 0))

        # Configuration
        cfg = self._card("Configuration")
        row1 = tk.Frame(cfg, bg=BG_CARD)
        row1.pack(fill="x", pady=(0, 4))
        tk.Label(row1, text="Server URL:", font=("Segoe UI", 10),
                 bg=BG_CARD, fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
        self.url_var = tk.StringVar(value="ws://85.184.250.25:3000/ws/driver")
        tk.Entry(row1, textvariable=self.url_var, font=("Consolas", 10),
                 bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat",
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", fill="x", expand=True, ipady=3)

        row2 = tk.Frame(cfg, bg=BG_CARD)
        row2.pack(fill="x", pady=(0, 8))
        tk.Label(row2, text="Interval (s):", font=("Segoe UI", 10),
                 bg=BG_CARD, fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
        self.interval_var = tk.StringVar(value="0.2")
        tk.Entry(row2, textvariable=self.interval_var, font=("Consolas", 10),
                 bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", width=6,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", ipady=3)

        self.connect_btn = tk.Button(
            cfg, text="Connect", font=("Segoe UI", 11, "bold"),
            bg=ACCENT, fg="#ffffff", activebackground="#4090df",
            activeforeground="#ffffff", relief="flat", cursor="hand2",
            command=self._on_connect_click)
        self.connect_btn.pack(fill="x", ipady=4)

        # Session
        ses = self._card("Session")
        self.code_var = tk.StringVar(value="------")
        self.pass_var = tk.StringVar(value="----")
        self._session_row(ses, "Code:", self.code_var)
        self._session_row(ses, "Password:", self.pass_var)

        status_row = tk.Frame(ses, bg=BG_CARD)
        status_row.pack(fill="x", pady=(4, 0))
        tk.Label(status_row, text="Status:", font=("Segoe UI", 10),
                 bg=BG_CARD, fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
        self.status_label = tk.Label(status_row, text="Disconnected",
                                     font=("Segoe UI", 10, "bold"),
                                     bg=BG_CARD, fg=RED)
        self.status_label.pack(side="left")

        # Telemetry
        tel = self._card("Telemetry")
        tgrid = tk.Frame(tel, bg=BG_CARD)
        tgrid.pack(fill="x")
        self.speed_var = tk.StringVar(value="---")
        self.gear_var = tk.StringVar(value="-")
        self.lap_var = tk.StringVar(value="-")
        self.fuel_var = tk.StringVar(value="-- L")
        self.fpl_var = tk.StringVar(value="--")
        self.laps_left_var = tk.StringVar(value="--")

        for col, (label, var) in enumerate([
            ("Speed", self.speed_var), ("Gear", self.gear_var),
            ("Lap", self.lap_var), ("Fuel", self.fuel_var),
        ]):
            tgrid.columnconfigure(col, weight=1)
            tk.Label(tgrid, text=label, font=("Segoe UI", 9),
                     bg=BG_CARD, fg=TEXT_DIM).grid(row=0, column=col)
            tk.Label(tgrid, textvariable=var, font=("Consolas", 20, "bold"),
                     bg=BG_CARD, fg=TEXT).grid(row=1, column=col)

        fuel_row = tk.Frame(tel, bg=BG_CARD)
        fuel_row.pack(fill="x", pady=(6, 0))
        tk.Label(fuel_row, text="Fuel/Lap:", font=("Segoe UI", 9),
                 bg=BG_CARD, fg=TEXT_DIM).pack(side="left")
        tk.Label(fuel_row, textvariable=self.fpl_var, font=("Consolas", 10),
                 bg=BG_CARD, fg=TEXT).pack(side="left", padx=(4, 16))
        tk.Label(fuel_row, text="Laps left:", font=("Segoe UI", 9),
                 bg=BG_CARD, fg=TEXT_DIM).pack(side="left")
        tk.Label(fuel_row, textvariable=self.laps_left_var, font=("Consolas", 10),
                 bg=BG_CARD, fg=TEXT).pack(side="left", padx=(4, 0))

        # Car & Track info
        info = self._card("Car & Track")
        self.car_var = tk.StringVar(value="--")
        self.track_var = tk.StringVar(value="--")
        self.compound_var = tk.StringVar(value="--")
        self.conditions_var = tk.StringVar(value="--")

        for lbl, var in [("Car:", self.car_var), ("Track:", self.track_var),
                         ("Compound:", self.compound_var), ("Conditions:", self.conditions_var)]:
            r = tk.Frame(info, bg=BG_CARD)
            r.pack(fill="x", pady=(0, 1))
            tk.Label(r, text=lbl, font=("Segoe UI", 9),
                     bg=BG_CARD, fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
            tk.Label(r, textvariable=var, font=("Consolas", 10),
                     bg=BG_CARD, fg=TEXT, anchor="w").pack(side="left", fill="x", expand=True)

        # Damage
        dmg_card = self._card("Car Damage")
        dmg_grid = tk.Frame(dmg_card, bg=BG_CARD)
        dmg_grid.pack(fill="x")
        self.dmg_vars = {}
        self.dmg_labels = {}
        for col, zone in enumerate(["Front", "Rear", "Left", "Right"]):
            dmg_grid.columnconfigure(col, weight=1)
            tk.Label(dmg_grid, text=zone, font=("Segoe UI", 9),
                     bg=BG_CARD, fg=TEXT_DIM).grid(row=0, column=col)
            v = tk.StringVar(value="0%")
            self.dmg_vars[zone.lower()] = v
            lbl = tk.Label(dmg_grid, textvariable=v, font=("Consolas", 14, "bold"),
                           bg=BG_CARD, fg=GREEN)
            lbl.grid(row=1, column=col)
            self.dmg_labels[zone.lower()] = lbl

        # Pit Strategy
        self.pit_frame = self._card("Pit Strategy (from Engineer)")
        self.pit_label = tk.Label(
            self.pit_frame, text="No strategy received yet.",
            font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_DIM,
            justify="left", anchor="w")
        self.pit_label.pack(fill="x")

        # Log
        log_card = self._card("Log", expand=True)
        self.log_text = tk.Text(
            log_card, font=("Consolas", 9), bg=BG, fg=TEXT_DIM,
            relief="flat", height=8, state="disabled", wrap="word",
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=BORDER, padx=6, pady=4)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_configure("info", foreground=TEXT_DIM)
        self.log_text.tag_configure("success", foreground=GREEN)
        self.log_text.tag_configure("warn", foreground=YELLOW)
        self.log_text.tag_configure("error", foreground=RED)

    def _card(self, title, expand=False):
        outer = tk.Frame(self.root, bg=BORDER)
        outer.pack(fill="both" if expand else "x", expand=expand,
                   padx=16, pady=(10, 0))
        inner = tk.Frame(outer, bg=BG_CARD)
        inner.pack(fill="both" if expand else "x", padx=1, pady=1)
        tk.Label(inner, text=title, font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_DIM, anchor="w").pack(fill="x", padx=8, pady=(6, 4))
        content = tk.Frame(inner, bg=BG_CARD)
        content.pack(fill="both" if expand else "x", expand=expand, padx=8, pady=(0, 8))
        return content

    def _session_row(self, parent, label, var):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", pady=(0, 2))
        tk.Label(row, text=label, font=("Segoe UI", 10),
                 bg=BG_CARD, fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
        entry = tk.Entry(row, textvariable=var, font=("Courier New", 20, "bold"),
                         bg=BG_CARD, fg=ACCENT, relief="flat", readonlybackground=BG_CARD,
                         state="readonly", width=10)
        entry.pack(side="left")

    # ── Status ───────────────────────────────────────────────────

    def _set_status(self, text, color):
        self.status_label.config(text=text, fg=color)

    # ── Logging ──────────────────────────────────────────────────

    def _log(self, message, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{ts}] {message}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ── Connect / Disconnect ─────────────────────────────────────

    def _on_connect_click(self):
        if self._running:
            self._do_disconnect()
        else:
            self._do_connect()

    def _do_connect(self):
        try:
            interval = float(self.interval_var.get())
        except ValueError:
            self._log("Invalid interval value.", "error")
            return
        if interval <= 0:
            self._log("Interval must be positive.", "error")
            return

        self._running = True
        self.connect_btn.config(text="Disconnect", bg=RED)
        self.url_var.trace_info()  # no-op, just to keep reference
        self._set_status("Connecting...", YELLOW)
        self._log("Connecting to server...")

        # Start asyncio thread
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        url = self.url_var.get().strip()
        self._connect_task = asyncio.run_coroutine_threadsafe(
            self._connect_loop(url, interval), self._loop)

    def _do_disconnect(self):
        self._running = False
        if self._connect_task:
            self._connect_task.cancel()
            self._connect_task = None
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._ac:
            self._ac.disconnect()
            self._ac = None
        self._ws = None
        self._last_fuel = None
        self._last_lap = None
        self._fuel_per_lap = 0

        self.connect_btn.config(text="Connect", bg=ACCENT)
        self._set_status("Disconnected", RED)
        self.code_var.set("------")
        self.pass_var.set("----")
        self._reset_telemetry()
        self._log("Disconnected.", "warn")

    def _reset_telemetry(self):
        self.speed_var.set("---")
        self.gear_var.set("-")
        self.lap_var.set("-")
        self.fuel_var.set("-- L")
        self.fpl_var.set("--")
        self.laps_left_var.set("--")
        self.car_var.set("--")
        self.track_var.set("--")
        self.compound_var.set("--")
        self.conditions_var.set("--")
        for zone in self.dmg_vars:
            self.dmg_vars[zone].set("0%")
            self.dmg_labels[zone].config(fg=GREEN)
        self.pit_label.config(text="No strategy received yet.", fg=TEXT_DIM)

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    # ── Async connection logic ───────────────────────────────────

    async def _connect_loop(self, url, interval):
        while self._running:
            try:
                async with websockets.connect(url) as ws:
                    self._ws = ws
                    self.root.after(0, self._set_status, "Connected", GREEN)
                    self.root.after(0, self._log, "Connected to server.", "success")

                    recv_task = asyncio.create_task(self._receive_loop(ws))
                    send_task = asyncio.create_task(self._send_loop(ws, interval))

                    done, pending = await asyncio.wait(
                        [recv_task, send_task],
                        return_when=asyncio.FIRST_COMPLETED)
                    for t in pending:
                        t.cancel()
                    self._ws = None

            except asyncio.CancelledError:
                return
            except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                self._ws = None
                self.root.after(0, self._set_status, "Connecting...", YELLOW)
                self.root.after(0, self._log,
                                f"Connection error: {e}. Retrying in 3s...", "error")
                await asyncio.sleep(3)

    async def _receive_loop(self, ws):
        async for raw in ws:
            if not self._running:
                return
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg["type"] == "session:created":
                code = msg["code"]
                password = msg["password"]
                self.root.after(0, self.code_var.set, code)
                self.root.after(0, self.pass_var.set, password)
                self.root.after(0, self._log,
                                f"Session created — Code: {code}", "success")

            elif msg["type"] == "pit:update":
                data = msg["data"]
                self.root.after(0, self._on_pit_update, data)

    async def _send_loop(self, ws, interval):
        ac_connected = False

        if self.mock:
            self._mock_telemetry = MockTelemetry()
            self.root.after(0, self._set_status, "Streaming (Mock)", GREEN)
            self.root.after(0, self._log, "Mock telemetry active.", "success")

            while self._running:
                data = self._mock_telemetry.tick(interval)
                data = self._apply_fuel_calc(data)
                await ws.send(json.dumps({"type": "telemetry", "data": data}))
                self.root.after(0, self._update_telemetry, data)
                await asyncio.sleep(interval)
            return

        # Real AC mode
        while self._running:
            if not ac_connected:
                if self._ac is None:
                    self._ac = ACTelemetry()
                if self._ac.connect():
                    ac_connected = True
                    self.root.after(0, self._set_status, "Streaming", GREEN)
                    self.root.after(0, self._log,
                                    "AC shared memory connected!", "success")
                else:
                    self.root.after(0, self._set_status, "Waiting for AC...", YELLOW)
                    await asyncio.sleep(1)
                    continue

            data = self._ac.read()
            if data is None:
                ac_connected = False
                self._ac.disconnect()
                self._ac = None
                self.root.after(0, self._set_status, "Waiting for AC...", YELLOW)
                self.root.after(0, self._log,
                                "Lost AC connection, retrying...", "warn")
                await asyncio.sleep(1)
                continue

            data = self._apply_fuel_calc(data)
            await ws.send(json.dumps({"type": "telemetry", "data": data}))
            self.root.after(0, self._update_telemetry, data)
            await asyncio.sleep(interval)

    def _apply_fuel_calc(self, data):
        """Prefer AC's fuelPerLap value, fall back to manual calculation."""
        current_lap = data.get("lap", 0)
        current_fuel = data.get("fuel", 0)

        if self._last_lap is not None and current_lap > self._last_lap:
            fuel_used = self._last_fuel - current_fuel
            if fuel_used > 0:
                self._fuel_per_lap = round(fuel_used, 2)
            self._last_fuel = current_fuel

        if self._last_lap is None or current_lap > self._last_lap:
            self._last_lap = current_lap
            if self._last_fuel is None:
                self._last_fuel = current_fuel

        ac_fpl = data.get("fuelPerLap", 0)
        data["fuelPerLap"] = ac_fpl if ac_fpl > 0 else self._fuel_per_lap
        return data

    # ── GUI update callbacks (main thread) ───────────────────────

    def _update_telemetry(self, data):
        speed = data.get("speed", 0)
        gear = data.get("gear", 0)
        if gear == 0:
            gear_str = "R"
        elif gear == 1:
            gear_str = "N"
        else:
            gear_str = str(gear - 1)

        fuel = data.get("fuel", 0)
        fpl = data.get("fuelPerLap", 0)

        self.speed_var.set(str(round(speed)))
        self.gear_var.set(gear_str)
        self.lap_var.set(str(data.get("lap", "-")))
        self.fuel_var.set(f"{fuel:.1f} L")
        self.fpl_var.set(f"{fpl:.2f}" if fpl > 0 else "--")

        if fpl > 0 and fuel > 0:
            self.laps_left_var.set(str(int(fuel / fpl)))
        else:
            self.laps_left_var.set("--")

        # Car & Track
        car = data.get("carModel", "")
        if car:
            self.car_var.set(car)
        track = data.get("track", "")
        cfg = data.get("trackConfig", "")
        if track:
            self.track_var.set(f"{track} — {cfg}" if cfg else track)

        compound = data.get("tyreCompound", "")
        if compound:
            self.compound_var.set(compound)

        air = data.get("airTemp")
        road = data.get("roadTemp")
        if air is not None and road is not None:
            self.conditions_var.set(f"Air {air}°C  Road {road}°C")

        # Damage: [front, rear, left, right, ?]
        dmg = data.get("carDamage", [0, 0, 0, 0, 0])
        zones = ["front", "rear", "left", "right"]
        for i, zone in enumerate(zones):
            val = dmg[i] if i < len(dmg) else 0
            self.dmg_vars[zone].set(f"{round(val)}%")
            if val < 5:
                color = GREEN
            elif val < 30:
                color = YELLOW
            elif val < 60:
                color = "#e3782c"
            else:
                color = RED
            self.dmg_labels[zone].config(fg=color)

    def _on_pit_update(self, data):
        fuel = data.get("fuel", 0)
        compound = data.get("tireCompound", "N/A")
        tires = "Yes" if data.get("changeTires") else "No"
        body = "Yes" if data.get("repairBody") else "No"
        engine = "Yes" if data.get("repairEngine") else "No"

        text = (f"Fuel: {fuel} L    Compound: {compound}\n"
                f"Change tires: {tires}    Body: {body}    Engine: {engine}")
        self.pit_label.config(text=text, fg=TEXT)
        self._log("Pit strategy update received!", "warn")
        self._flash_pit(0)

    def _flash_pit(self, count):
        if count >= 6:
            self.pit_frame.master.master.config(bg=BORDER)
            return
        color = YELLOW if count % 2 == 0 else RED
        self.pit_frame.master.master.config(bg=color)
        self.root.after(250, self._flash_pit, count + 1)

    # ── Window close ─────────────────────────────────────────────

    def _on_close(self):
        self._running = False
        if self._connect_task:
            self._connect_task.cancel()
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._ac:
            self._ac.disconnect()
        self.root.destroy()

    # ── Run ──────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Easy Engineer — Host GUI")
    parser.add_argument("--mock", action="store_true",
                        help="Use mock telemetry instead of AC shared memory")
    parser.add_argument("--server", default=None,
                        help="Pre-fill server URL")
    args = parser.parse_args()

    app = HostApp(mock=args.mock)

    if args.server:
        app.url_var.set(args.server)

    if args.mock:
        app._log("Mock mode enabled — will use fake telemetry.", "warn")

    app.run()


if __name__ == "__main__":
    main()
