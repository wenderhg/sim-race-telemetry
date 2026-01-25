from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class TelemetryData:
    throttle: float = 0.0  # 0.0 to 1.0
    brake: float = 0.0     # 0.0 to 1.0
    clutch: float = 0.0    # 0.0 to 1.0
    rpm: float = 0.0
    speed_kph: float = 0.0
    steering_angle: float = 0.0 # radians, 0 = center, positive = left? Need to check convention. Usually CCW is positive.
    gear: int = 0          # 0 = N, -1 = R, 1-N = Gears
    active: bool = False   # True if game is active/driving

class GameAdapter(ABC):
    @abstractmethod
    def update(self) -> TelemetryData:
        """Called periodically to fetch the latest telemetry state."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the adapter (e.g., 'iRacing')."""
        pass
