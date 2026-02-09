import sys
import os
import time

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telemetry.adapters.assetto_corsa import AssettoCorsaAdapter

def main():
    print("Initializing AC Adapter...")
    adapter = AssettoCorsaAdapter()
    
    print("Waiting for connection (Press Ctrl+C to stop)...")
    try:
        while True:
            data = adapter.update()
            if adapter.connected:
                print(f"\rConnected! RPM: {data.rpm:.0f}, Speed: {data.speed_kph:.0f} km/h, Gear: {data.gear}, Active: {data.active}    ", end='')
            else:
                print("\rNot connected. Waiting...    ", end='')
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
