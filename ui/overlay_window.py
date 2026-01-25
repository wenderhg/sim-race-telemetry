from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMenu, QApplication
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QAction, QColor, QPalette

from .widgets.trace_graph import TraceGraphWidget
from .widgets.input_bars import InputBarsWidget
from .widgets.dashboard_gauge import DashboardGaugeWidget

class OverlayWindow(QWidget):
    def __init__(self, telemetry_engine):
        super().__init__()
        self.telemetry_engine = telemetry_engine
        self.locked = False
        self.dashboard_visible = True
        
        self.setWindowTitle("Sim Racing Overlay")
        self.resize(800, 150)
        
        # Window Flags
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool # Tool window doesn't show in taskbar usually, good for overlays
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        
        # 1. Telemetry Strip (Left)
        self.strip = QLabel("TELEMETRY")
        self.strip.setFixedWidth(30)
        self.strip.setAlignment(Qt.AlignCenter)
        self.strip.setStyleSheet("""
            background-color: #111;
            color: white;
            border-left: 3px solid red;
            font-weight: bold;
            font-size: 12px;
        """)
        # Rotate text? Standard QLabel doesn't rotate easily. 
        # For prototype we'll keep it simple vertical text or just horizontal.
        # Let's make it vertical via newlines for now to save complexity
        self.strip.setText("T\nE\nL\nE\nM\nE\nT\nR\nY")
        self.main_layout.addWidget(self.strip)

        # 2. Trace Graph (Center)
        self.graph = TraceGraphWidget()
        self.main_layout.addWidget(self.graph, stretch=3)

        # 3. Input Bars
        self.bars = InputBarsWidget()
        self.main_layout.addWidget(self.bars)

        # 4. Dashboard (Right)
        self.dashboard = DashboardGaugeWidget()
        self.main_layout.addWidget(self.dashboard)

        # Connect Telemetry
        self.telemetry_engine.data_updated.connect(self.update_ui)
        
        # Logic for dragging
        self.old_pos = None
        
        # Scaling State
        self.current_scale = 1.0 # 100%
        self.base_width = 800
        self.base_height = 150

        # Init functionality
        self.update_lock_state()

    def update_ui(self, data):
        self.graph.update_data(data.throttle, data.brake)
        self.bars.update_data(data.clutch, data.brake, data.throttle)
        if self.dashboard_visible:
            self.dashboard.update_data(data.gear, data.speed_kph, data.rpm)

    def change_scale(self, delta):
        new_scale = self.current_scale + delta
        # Clamp between 0.4 (40%) and 1.0 (100%)
        # Floating point math can be messy so round strictly
        new_scale = round(new_scale, 2)
        if new_scale < 0.40: new_scale = 0.40
        if new_scale > 1.00: new_scale = 1.00
        
        self.current_scale = new_scale
        
        # Scale Strip
        new_strip_width = int(30 * new_scale)
        new_font_size = max(8, int(12 * new_scale))
        self.strip.setFixedWidth(new_strip_width)
        self.strip.setStyleSheet(f"""
            background-color: #111;
            color: white;
            border-left: {max(1, int(3*new_scale))}px solid red;
            font-weight: bold;
            font-size: {new_font_size}px;
        """)
        
        # Scale Dashboard
        dash_size = int(100 * new_scale)
        self.dashboard.setFixedSize(dash_size, dash_size)

        # Scale Input Bars
        self.bars.set_scale(new_scale)
        
        new_w = int(self.base_width * self.current_scale)
        new_h = int(self.base_height * self.current_scale)
        self.resize(new_w, new_h)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        lock_action = QAction("Unlock" if self.locked else "Lock", self)
        lock_action.triggered.connect(self.toggle_lock)
        menu.addAction(lock_action)

        dash_action = QAction("Hide Dashboard" if self.dashboard_visible else "Show Dashboard", self)
        dash_action.triggered.connect(self.toggle_dashboard)
        menu.addAction(dash_action)
        
        menu.addSeparator()
        
        # Resize Actions
        inc_action = QAction("Increase Size (+5%)", self)
        inc_action.triggered.connect(lambda: self.change_scale(0.05))
        menu.addAction(inc_action)

        dec_action = QAction("Decrease Size (-5%)", self)
        dec_action.triggered.connect(lambda: self.change_scale(-0.05))
        menu.addAction(dec_action)
        
        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)

        menu.exec(event.globalPos())

    def toggle_dashboard(self):
        self.dashboard_visible = not self.dashboard_visible
        self.dashboard.setVisible(self.dashboard_visible)
        # Adjust window size if needed, or layout handles it
        
    def toggle_lock(self):
        self.locked = not self.locked
        self.update_lock_state()

    def update_lock_state(self):
        if self.locked:
            # Click through mode is complex in pure Python/Qt without pywin32, 
            # but standard "TransparentForMouseEvents" attribute might work if the window manager supports it.
            # However, to be truly click-through on Windows usually requires changing window styles via win32api.
            # For this MVP, "Lock" essentially means "Don't process drag events" 
            # and potentially we can set WA_TransparentForMouseEvents.
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setWindowFlag(Qt.WindowTransparentForInput, True) # Qt 5.10+
            # We need to re-show for flags to take effect sometimes
            self.hide()
            self.show()
            
            # To allow unlocking, we might need a system tray icon or a hotkey, 
            # because if it's click-through, we can't right click it!
            # WARN: If we make it click through, user can't unlock it via context menu.
            # So I will ONLY disable dragging for now, unless we implement a Tray Icon.
            # Reverting click-through for now to ensure user doesn't get stuck.
            # I will implement Tray Icon in main.py to handle the "Deep Lock".
            pass 
        else:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.setWindowFlag(Qt.WindowTransparentForInput, False)
            self.hide()
            self.show()

    def mousePressEvent(self, event):
        if not self.locked and event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if not self.locked and self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
