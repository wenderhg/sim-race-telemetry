import sys
import threading
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

from PySide6.QtCore import Qt
from telemetry.telemetry_engine import TelemetryEngine
from ui.overlay_window import OverlayWindow

def main():
    app = QApplication(sys.argv)
    
    # Create Telemetry Backend
    engine = TelemetryEngine()
    engine.start()
    
    # Create Overlay
    window = OverlayWindow(engine)
    window.show()
    
    # System Tray Logic (To allow Unlocking if window is click-through)
    tray = QSystemTrayIcon(app)
    
    # Generate a simple icon programmatically so it's visible
    from PySide6.QtGui import QPixmap, QPainter, QColor
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor(0, 255, 0)) # Green
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, 16, 16)
    painter.end()
    tray.setIcon(QIcon(pixmap))
    
    tray_menu = QMenu()
    
    action_lock = QAction("Toggle Lock / Click-Through", app)
    action_lock.triggered.connect(window.toggle_lock)
    tray_menu.addAction(action_lock)
    
    action_exit = QAction("Exit", app)
    action_exit.triggered.connect(app.quit)
    tray_menu.addAction(action_exit)
    
    tray.setContextMenu(tray_menu)
    tray.show()

    ret = app.exec()
    engine.stop()
    sys.exit(ret)

if __name__ == "__main__":
    main()
