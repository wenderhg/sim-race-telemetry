from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor

class DashboardGaugeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100) 
        
        self.gear = 0
        self.speed = 0
        self.rpm_pct = 0.0 # 0.0 to 1.0

        self.setStyleSheet("background-color: transparent;")

    def update_data(self, gear, speed, rpm, max_rpm=8000):
        self.gear = gear
        self.speed = int(speed)
        self.rpm_pct = min(1.0, rpm / max_rpm)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Determine the scale based on the actual widget size vs logical size (100x100)
        side = min(self.width(), self.height())
        scale = side / 100.0
        
        # Center the drawing
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(scale, scale)
        painter.translate(-50, -50) # Move origin back to top-left of logical 100x100 box
        
        # Now drawing in logical coordinates (0,0) to (100,100)
        rect = self.rect() # Accessing standard rect might be wrong if we scaled. 
        # But wait, self.rect() returns the widget size (e.g. 50x50), not logical size.
        # We need a logical rect.
        logical_rect = QRect(0, 0, 100, 100)
        
        c = QPoint(50, 50)
        radius = 45 # 100/2 - 5
        
        # Background Circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 200))
        painter.drawEllipse(c, radius, radius)
        
        # RPM Arc (Background)
        painter.setPen(QPen(QColor(50, 50, 50), 6))
        painter.setBrush(Qt.NoBrush)
        # 10,10,-10,-10 inset from 0,0,100,100 -> 10,10 width 80 height 80
        arc_rect = logical_rect.adjusted(10, 10, -10, -10)
        painter.drawArc(arc_rect, -45 * 16, 270 * 16)

        # RPM Arc (Active)
        color = QColor(0, 255, 0)
        if self.rpm_pct > 0.8: color = QColor(255, 0, 0)
        elif self.rpm_pct > 0.5: color = QColor(255, 255, 0)
        
        painter.setPen(QPen(color, 6))
        start_angle = 225 * 16
        span_angle = - (self.rpm_pct * 270) * 16
        painter.drawArc(arc_rect, start_angle, span_angle)

        # Text Drawing
        painter.setPen(QColor(255, 255, 255))
        
        # Gear (Top half, smaller)
        f = painter.font()
        f.setPixelSize(24)
        f.setBold(True)
        painter.setFont(f)
        
        gear_str = "N" if self.gear == 0 else "R" if self.gear == -1 else str(self.gear)
        painter.drawText(logical_rect.translated(0, -20), Qt.AlignCenter, gear_str)

        # Speed (Bottom half, larger)
        f.setPixelSize(22)
        f.setBold(True)
        painter.setFont(f)
        painter.drawText(logical_rect.translated(0, 12), Qt.AlignCenter, str(self.speed))

        # Unit label (kph)
        f.setPixelSize(10)
        f.setBold(False)
        painter.setFont(f)
        painter.drawText(logical_rect.translated(0, 34), Qt.AlignCenter, "kph")
