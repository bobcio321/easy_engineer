"""Assetto Corsa shared memory structures (ctypes definitions).

Based on AC shared memory documentation.
Memory-mapped files:
  - acpmf_physics   -> SPageFilePhysics
  - acpmf_graphics  -> SPageFileGraphics
  - acpmf_static    -> SPageFileStatic
"""

import ctypes
import mmap


class SPageFilePhysics(ctypes.Structure):
    _fields_ = [
        ("packetId", ctypes.c_int),
        ("gas", ctypes.c_float),
        ("brake", ctypes.c_float),
        ("fuel", ctypes.c_float),
        ("gear", ctypes.c_int),
        ("rpms", ctypes.c_int),
        ("steerAngle", ctypes.c_float),
        ("speedKmh", ctypes.c_float),
        ("velocity", ctypes.c_float * 3),
        ("accG", ctypes.c_float * 3),
        ("wheelSlip", ctypes.c_float * 4),
        ("wheelLoad", ctypes.c_float * 4),
        ("wheelsPressure", ctypes.c_float * 4),
        ("wheelAngularSpeed", ctypes.c_float * 4),
        ("tyreWear", ctypes.c_float * 4),
        ("tyreDirtyLevel", ctypes.c_float * 4),
        ("tyreCoreTemperature", ctypes.c_float * 4),
        ("camberRAD", ctypes.c_float * 4),
        ("suspensionTravel", ctypes.c_float * 4),
        ("drs", ctypes.c_float),
        ("tc", ctypes.c_float),
        ("heading", ctypes.c_float),
        ("pitch", ctypes.c_float),
        ("roll", ctypes.c_float),
        ("cgHeight", ctypes.c_float),
        ("carDamage", ctypes.c_float * 5),
        ("numberOfTyresOut", ctypes.c_int),
        ("pitLimiterOn", ctypes.c_int),
        ("abs", ctypes.c_float),
        ("kersCharge", ctypes.c_float),
        ("kersInput", ctypes.c_float),
        ("autoShifterOn", ctypes.c_int),
        ("rideHeight", ctypes.c_float * 2),
        ("turboBoost", ctypes.c_float),
        ("ballast", ctypes.c_float),
        ("airDensity", ctypes.c_float),
        ("airTemp", ctypes.c_float),
        ("roadTemp", ctypes.c_float),
        ("localAngularVel", ctypes.c_float * 3),
        ("finalFF", ctypes.c_float),
        ("performanceMeter", ctypes.c_float),
        ("engineBrake", ctypes.c_int),
        ("ersRecoveryLevel", ctypes.c_int),
        ("ersPowerLevel", ctypes.c_int),
        ("ersHeatCharging", ctypes.c_int),
        ("ersIsCharging", ctypes.c_int),
        ("kersCurrentKJ", ctypes.c_float),
        ("drsAvailable", ctypes.c_int),
        ("drsEnabled", ctypes.c_int),
        ("brakeTemp", ctypes.c_float * 4),
        ("clutch", ctypes.c_float),
        ("tyreTempI", ctypes.c_float * 4),
        ("tyreTempM", ctypes.c_float * 4),
        ("tyreTempO", ctypes.c_float * 4),
        ("isAIControlled", ctypes.c_int),
        ("tyreContactPoint", ctypes.c_float * 4 * 3),
        ("tyreContactNormal", ctypes.c_float * 4 * 3),
        ("tyreContactHeading", ctypes.c_float * 4 * 3),
        ("brakeBias", ctypes.c_float),
        ("localVelocity", ctypes.c_float * 3),
    ]


class SPageFileGraphics(ctypes.Structure):
    _fields_ = [
        ("packetId", ctypes.c_int),
        ("status", ctypes.c_int),  # AC_OFF=0, AC_REPLAY=1, AC_LIVE=2, AC_PAUSE=3
        ("session", ctypes.c_int),
        ("currentTime", ctypes.c_wchar * 15),
        ("lastTime", ctypes.c_wchar * 15),
        ("bestTime", ctypes.c_wchar * 15),
        ("split", ctypes.c_wchar * 15),
        ("completedLaps", ctypes.c_int),
        ("position", ctypes.c_int),
        ("iCurrentTime", ctypes.c_int),
        ("iLastTime", ctypes.c_int),
        ("iBestTime", ctypes.c_int),
        ("sessionTimeLeft", ctypes.c_float),
        ("distanceTraveled", ctypes.c_float),
        ("isInPit", ctypes.c_int),
        ("currentSectorIndex", ctypes.c_int),
        ("lastSectorTime", ctypes.c_int),
        ("numberOfLaps", ctypes.c_int),
        ("tyreCompound", ctypes.c_wchar * 33),
        ("replayTimeMultiplier", ctypes.c_float),
        ("normalizedCarPosition", ctypes.c_float),
        ("activeCars", ctypes.c_int),
        ("carCoordinates", ctypes.c_float * 60 * 3),
        ("carID", ctypes.c_int),
        ("playerCarID", ctypes.c_int),
        ("penaltyTime", ctypes.c_float),
        ("flag", ctypes.c_int),
        ("penalty", ctypes.c_int),
        ("idealLineOn", ctypes.c_int),
        ("isInPitLane", ctypes.c_int),
        ("surfaceGrip", ctypes.c_float),
        ("mandatoryPitDone", ctypes.c_int),
        ("windSpeed", ctypes.c_float),
        ("windDirection", ctypes.c_float),
        ("isSetupMenuVisible", ctypes.c_int),
        ("mainDisplayIndex", ctypes.c_int),
        ("secondaryDisplayIndex", ctypes.c_int),
        ("TC", ctypes.c_int),
        ("TCCut", ctypes.c_int),
        ("EngineMap", ctypes.c_int),
        ("ABS", ctypes.c_int),
        ("fuelXLap", ctypes.c_float),
        ("rainLights", ctypes.c_int),
        ("flashingLights", ctypes.c_int),
        ("lightsStage", ctypes.c_int),
        ("exhaustTemperature", ctypes.c_float),
        ("wiperLV", ctypes.c_int),
        ("driverStintTotalTimeLeft", ctypes.c_int),
        ("driverStintTimeLeft", ctypes.c_int),
        ("rainTyres", ctypes.c_int),
    ]


class SPageFileStatic(ctypes.Structure):
    _fields_ = [
        ("smVersion", ctypes.c_wchar * 15),
        ("acVersion", ctypes.c_wchar * 15),
        ("numberOfSessions", ctypes.c_int),
        ("numCars", ctypes.c_int),
        ("carModel", ctypes.c_wchar * 33),
        ("track", ctypes.c_wchar * 33),
        ("playerName", ctypes.c_wchar * 33),
        ("playerSurname", ctypes.c_wchar * 33),
        ("playerNick", ctypes.c_wchar * 33),
        ("sectorCount", ctypes.c_int),
        ("maxTorque", ctypes.c_float),
        ("maxPower", ctypes.c_float),
        ("maxRpm", ctypes.c_int),
        ("maxFuel", ctypes.c_float),
        ("suspensionMaxTravel", ctypes.c_float * 4),
        ("tyreRadius", ctypes.c_float * 4),
        ("maxTurboBoost", ctypes.c_float),
        ("deprecated1", ctypes.c_float),
        ("deprecated2", ctypes.c_float),
        ("penaltiesEnabled", ctypes.c_int),
        ("aidFuelRate", ctypes.c_float),
        ("aidTireRate", ctypes.c_float),
        ("aidMechanicalDamage", ctypes.c_float),
        ("aidAllowTyreBlankets", ctypes.c_int),
        ("aidStability", ctypes.c_float),
        ("aidAutoClutch", ctypes.c_int),
        ("aidAutoBlip", ctypes.c_int),
        ("hasDRS", ctypes.c_int),
        ("hasERS", ctypes.c_int),
        ("hasKERS", ctypes.c_int),
        ("kersMaxJ", ctypes.c_float),
        ("engineBrakeSettingsCount", ctypes.c_int),
        ("ersPowerControllerCount", ctypes.c_int),
        ("trackSPlineLength", ctypes.c_float),
        ("trackConfiguration", ctypes.c_wchar * 33),
        ("ersMaxJ", ctypes.c_float),
        ("isTimedRace", ctypes.c_int),
        ("hasExtraLap", ctypes.c_int),
        ("carSkin", ctypes.c_wchar * 33),
        ("reversedGridPositions", ctypes.c_int),
        ("pitWindowStart", ctypes.c_int),
        ("pitWindowEnd", ctypes.c_int),
        ("isOnline", ctypes.c_int),
    ]


class ACTelemetry:
    """Reads Assetto Corsa telemetry from shared memory."""

    def __init__(self):
        self._physics_mmap = None
        self._graphics_mmap = None
        self._static_mmap = None
        self._connected = False

    def connect(self):
        """Open shared memory mapped files. Returns True if successful."""
        try:
            self._physics_mmap = mmap.mmap(
                -1, ctypes.sizeof(SPageFilePhysics), "acpmf_physics"
            )
            self._graphics_mmap = mmap.mmap(
                -1, ctypes.sizeof(SPageFileGraphics), "acpmf_graphics"
            )
            self._static_mmap = mmap.mmap(
                -1, ctypes.sizeof(SPageFileStatic), "acpmf_static"
            )
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def disconnect(self):
        for m in (self._physics_mmap, self._graphics_mmap, self._static_mmap):
            if m:
                m.close()
        self._connected = False

    def _read_struct(self, mm, struct_type):
        mm.seek(0)
        data = mm.read(ctypes.sizeof(struct_type))
        return struct_type.from_buffer_copy(data)

    def read(self):
        """Read current telemetry. Returns dict or None if not connected."""
        if not self._connected:
            return None

        try:
            physics = self._read_struct(self._physics_mmap, SPageFilePhysics)
            graphics = self._read_struct(self._graphics_mmap, SPageFileGraphics)
            static = self._read_struct(self._static_mmap, SPageFileStatic)

            return {
                "speed": round(physics.speedKmh, 1),
                "fuel": round(physics.fuel, 2),
                "gear": physics.gear,
                "rpm": physics.rpms,
                "maxRpm": static.maxRpm,
                "maxFuel": round(static.maxFuel, 1),
                "tireTemp": [round(t, 1) for t in physics.tyreCoreTemperature],
                "tireWear": [round(w, 1) for w in physics.tyreWear],
                "tirePressure": [round(p, 1) for p in physics.wheelsPressure],
                "brakeTemp": [round(t, 1) for t in physics.brakeTemp],
                "lap": graphics.completedLaps + 1,
                "lastLap": graphics.iLastTime,
                "bestLap": graphics.iBestTime,
                "currentLap": graphics.iCurrentTime,
                "fuelPerLap": round(graphics.fuelXLap, 2),
                "carModel": static.carModel.rstrip('\x00'),
                "carSkin": static.carSkin.rstrip('\x00'),
                "track": static.track.rstrip('\x00'),
                "trackConfig": static.trackConfiguration.rstrip('\x00'),
                "tyreCompound": graphics.tyreCompound.rstrip('\x00'),
                "carDamage": [round(d, 2) for d in physics.carDamage],
                "abs": round(physics.abs, 2),
                "tc": round(physics.tc, 2),
                "drs": int(physics.drsEnabled),
                "pitLimiter": int(physics.pitLimiterOn),
                "isInPit": int(graphics.isInPit),
                "isInPitLane": int(graphics.isInPitLane),
                "position": graphics.position,
                "numberOfLaps": graphics.numberOfLaps,
                "sessionTimeLeft": round(graphics.sessionTimeLeft, 1),
                "airTemp": round(physics.airTemp, 1),
                "roadTemp": round(physics.roadTemp, 1),
                "maxPower": round(static.maxPower, 1),
                "maxTorque": round(static.maxTorque, 1),
                "hasDRS": int(static.hasDRS),
                "hasERS": int(static.hasERS),
                "hasKERS": int(static.hasKERS),
                "aidMechanicalDamage": round(static.aidMechanicalDamage, 2),
                "rainTyres": int(graphics.rainTyres),
            }
        except Exception:
            return None
