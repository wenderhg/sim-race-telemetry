import irsdk
from .base import GameAdapter, TelemetryData

class IRacingAdapter(GameAdapter):
    def __init__(self):
        self.ir = irsdk.IRSDK()
        self.connected = False

    @property
    def name(self) -> str:
        return "iRacing"

    def update(self) -> TelemetryData:
        # Check connection on every update
        if not self.connected:
            self.connected = self.ir.startup()
            if not self.connected:
                # Return empty/default data if not connected
                return TelemetryData(active=False)

        # Still connected?
        if not self.ir.is_initialized:
            self.connected = False
            return TelemetryData(active=False)

        # Read Data
        # iRacing gives inputs as 0.0-1.0 usually
        throttle = self.ir['Throttle'] or 0.0
        brake = self.ir['Brake'] or 0.0
        clutch = 1.0 - (self.ir['Clutch'] or 0.0) # iRacing clutch is inverted? Needs verification. 
        # Usually Clutch is 1.0 pushed, 0.0 released. But sometimes 0.0 pushed.
        # Let's assume standard 0-1. If needed we flip.
        # Actually iRacing Clutch: 0.0 is released, 1.0 is fully pressed. 
        # But 'Clutch' in telemetry often raw pedal?
        # Let's stick to raw.
        clutch = self.ir['Clutch'] or 0.0
        
        rpm = self.ir['RPM'] or 0.0
        speed_ms = self.ir['Speed'] or 0.0
        speed_kph = speed_ms * 3.6
        
        gear = self.ir['Gear'] or 0
        # iRacing Gears: -1 = Reverse, 0 = Neutral, 1-N = Forward
        
        # Steering Angle
        # iRacing 'SteeringWheelAngle' is in radians. Positive is usually left (CCW).
        steering_angle = self.ir['SteeringWheelAngle'] or 0.0
        
        is_on_track = self.ir['IsOnTrack']
        
        return TelemetryData(
            throttle=throttle,
            brake=brake,
            clutch=clutch,
            rpm=rpm,
            speed_kph=speed_kph,
            gear=gear,
            steering_angle=steering_angle,
            active=bool(is_on_track)
        )
