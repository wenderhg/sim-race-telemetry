import time
import threading
from PySide6.QtCore import QObject, Signal
from .adapters.base import GameAdapter, TelemetryData
from .adapters.mock import MockAdapter
from .adapters.iracing import IRacingAdapter
from .adapters.assetto_corsa import AssettoCorsaAdapter

class TelemetryEngine(QObject):
    data_updated = Signal(object) # Emits TelemetryData

    def __init__(self):
        super().__init__()
        # Initialize adapters list
        self.mock_adapter = MockAdapter()
        self.iracing_adapter = IRacingAdapter()
        self.ac_adapter = AssettoCorsaAdapter()
        
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
            
            # Auto-detection logic
            
            # 1. Check iRacing
            if not self.iracing_adapter.connected:
                # Try to connect
                self.iracing_adapter.update() 
            
            if self.iracing_adapter.connected:
                data = self.iracing_adapter.update()
            
            # 2. Check Assetto Corsa (if iRacing not active)
            if not data:
                if not self.ac_adapter.connected:
                    self.ac_adapter.update() # Try connect
                
                if self.ac_adapter.connected:
                    data = self.ac_adapter.update()

            # 3. Fallback to Mock
            if not data:
                # Fallback to Mock so we have visuals
                data = self.mock_adapter.update()

            if data:
                self.data_updated.emit(data)

            elapsed = time.time() - start_time
            sleep_time = max(0, (1.0 / 60.0) - elapsed)
            time.sleep(sleep_time)
