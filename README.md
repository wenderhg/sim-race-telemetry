# Sim Race Telemetry

A real-time telemetry overlay for sim racing, featuring a dashboard, input visualization, and live trace graphs.

## Features

-   **Dashboard**: Displays Gear, Speed, RPM, and active flags.
-   **Input Telemetry**: Visual bars for Throttle, Brake, and Clutch.
-   **Trace Graph**: Real-time graph showing throttle and brake traces.
-   **Supported Games**:
    -   iRacing
    -   Assetto Corsa
    -   (Mock mode for testing)

## Requirements

-   **OS**: Windows 10/11
-   **Python**: 3.10+

## Installation

1.  Clone the repository or download the source code.
2.  Install dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

    *If you don't have a `requirements.txt` yet, manually install:*
    ```bash
    pip install PySide6 irsdk
    ```

## Usage

1.  Start your Simulator (iRacing or Assetto Corsa) first.
2.  Run the main application:

    ```bash
    python main.py
    ```

### Desktop Mode
-   The overlay window is "Always on Top".
-   **Drag** the window to position it.
-   **Right-Click** the window to access the menu:
    -   **Lock/Unlock**: Lock the window position.
    -   **Resize**: Scale the overlay size up or down.
    -   **Hide Dashboard**: Toggle the gauge view.

## Troubleshooting

-   **Game not detected**:
    -   Ensure the game is supported and running.
    -   For Assetto Corsa, ensure Shared Memory is enabled in settings (usually on by default).

## License
[MIT](LICENSE)
