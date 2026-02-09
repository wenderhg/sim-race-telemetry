import mmap
import ctypes
import time
from .base import GameAdapter, TelemetryData
from .ac_types import SPageFilePhysics, SPageFileGraphics, SPageFileStatic, AC_STATUS_PAUSE, AC_STATUS_LIVE, AC_STATUS_REPLAY

class AssettoCorsaAdapter(GameAdapter):
    def __init__(self):
        self._physics_mm = None
        self._graphics_mm = None
        self._static_mm = None
        self._connected = False
        self._last_connect_attempt = 0
        self.static_data = None # Cache static data

    @property
    def name(self) -> str:
        return "Assetto Corsa"

    @property
    def connected(self) -> bool:
        return self._connected

    def _connect(self):
        # Rate limit connection attempts
        if time.time() - self._last_connect_attempt < 2.0:
            return False
        
        self._last_connect_attempt = time.time()

        try:
            # AC uses specific shared memory names
            self._physics_mm = mmap.mmap(-1, ctypes.sizeof(SPageFilePhysics), tagname="Local\\acpmf_physics", access=mmap.ACCESS_READ)
            self._graphics_mm = mmap.mmap(-1, ctypes.sizeof(SPageFileGraphics), tagname="Local\\acpmf_graphics", access=mmap.ACCESS_READ)
            self._static_mm = mmap.mmap(-1, ctypes.sizeof(SPageFileStatic), tagname="Local\\acpmf_static", access=mmap.ACCESS_READ)
            
            # If we got here, we connected. Read static data once.
            self.static_data = SPageFileStatic.from_buffer_copy(self._static_mm)
            self._connected = True
            return True
        except FileNotFoundError:
            # Game probably not running
            self._connected = False
            return False
        except Exception as e:
            print(f"Failed to connect to AC shared memory: {e}")
            self._connected = False
            return False

    def _disconnect(self):
        if self._physics_mm: self._physics_mm.close()
        if self._graphics_mm: self._graphics_mm.close()
        if self._static_mm: self._static_mm.close()
        self._physics_mm = None
        self._graphics_mm = None
        self._static_mm = None
        self.static_data = None
        self._connected = False

    def update(self) -> TelemetryData:
        if not self._connected:
            if not self._connect():
                return TelemetryData() # Return empty if not connected

        try:
            # Read from shared memory
            self._physics_mm.seek(0)
            physics = SPageFilePhysics.from_buffer_copy(self._physics_mm)
            
            self._graphics_mm.seek(0)
            graphics = SPageFileGraphics.from_buffer_copy(self._graphics_mm)

            # Map to TelemetryData
            
            # AC Gear: 0=R, 1=N, 2=1st, etc... Wait, let's verify standard AC gear mapping.
            # Usually: 0=R, 1=N, 2=1, 3=2...
            # TelemetryData expects: 0 = N, -1 = R, 1 = 1st
            gear_raw = physics.gear
            if gear_raw == 0:
                gear = -1
            elif gear_raw == 1:
                gear = 0
            else:
                gear = gear_raw - 1

            # Check if active
            is_active = graphics.status == AC_STATUS_LIVE
            
            # Steering angle: AC is in degrees or radians? 
            # Note says "radians" in TelemetryData.
            # ac_types has 'steerAngle' (float). In AC it is usually radians.
            
            return TelemetryData(
                throttle=physics.gas,
                brake=physics.brake,
                clutch=physics.clutch, # physics.clutch is available
                rpm=float(physics.rpms),
                speed_kph=physics.speedKmh,
                steering_angle=-physics.steerAngle, 
                gear=gear,
                active=is_active
            )

        except Exception as e:
            # If reading fails, maybe game closed or crashed
            print(f"Error reading AC shared memory: {e}")
            self._disconnect()
            return TelemetryData()
