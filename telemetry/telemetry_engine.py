import time
import threading
from PySide6.QtCore import QObject, Signal
from .adapters.base import GameAdapter, TelemetryData
from .adapters.mock import MockAdapter
from .adapters.iracing import IRacingAdapter

class TelemetryEngine(QObject):
    data_updated = Signal(object) # Emits TelemetryData

    def __init__(self):
        super().__init__()
        # Initialize adapters list
        self.mock_adapter = MockAdapter()
        self.iracing_adapter = IRacingAdapter()
        
        # Default to Mock, but we can have a logic to auto-switch
        # For this stage, let's use a simple strategy:
        # If iRacing is connected (startup returns true), use it.
        # Otherwise use Mock.
        self.adapter: GameAdapter = self.iracing_adapter 

        self.running = False
        self._thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._pollen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()

    def set_adapter(self, adapter: GameAdapter):
        self.adapter = adapter

    def _pollen_loop(self):
        while self.running:
            # Poll at 60Hz
            start_time = time.time()
            
            data = None
            
            # Auto-detection logic (simplified)
            # Check iRacing
            if not self.iracing_adapter.connected:
                # Try to connect
                self.iracing_adapter.update() # This attempts startup inside
            
            if self.iracing_adapter.connected:
                data = self.iracing_adapter.update()
                if not data.active:
                    # Connected but not on track could still be valid, or maybe fallback?
                    # Let's show the data even if not active (e.g. in pits)
                    pass
            else:
                # Fallback to Mock so we have visuals
                data = self.mock_adapter.update()
                # Indicate it's mock data? We might want a UI flag, but for now just show it.

            if data:
                self.data_updated.emit(data)

            elapsed = time.time() - start_time
            sleep_time = max(0, (1.0 / 60.0) - elapsed)
            time.sleep(sleep_time)
