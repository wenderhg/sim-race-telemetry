import math
import time
import random
from .base import GameAdapter, TelemetryData

class MockAdapter(GameAdapter):
    def __init__(self):
        self.start_time = time.time()
        self.gear = 1
        self.speed = 0.0

    @property
    def name(self) -> str:
        return "Mock Simulator"

    def update(self) -> TelemetryData:
        t = time.time() - self.start_time
        
        # Simulate throttle with a sine wave
        throttle = (math.sin(t) + 1) / 2
        
        # Simulate brake with a shifted sine wave, clamped
        brake = max(0, math.sin(t + 2)) * 0.8
        
        # Clutch random spikes
        clutch = 0.0 if random.random() > 0.1 else random.random() * 0.5
        
        # RPM revving up and down
        rpm = 1000 + (throttle * 7000)
        
        # Speed following throttle roughly
        self.speed = self.speed * 0.95 + (throttle * 200) * 0.05
        
        # Simple auto gear shift simulation for display
        if self.speed < 20: self.gear = 1
        elif self.speed < 50: self.gear = 2
        elif self.speed < 90: self.gear = 3
        elif self.speed < 130: self.gear = 4
        else: self.gear = 5

        return TelemetryData(
            throttle=throttle,
            brake=brake,
            clutch=clutch,
            rpm=rpm,
            speed_kph=self.speed,
            gear=self.gear,
            active=True
        )
