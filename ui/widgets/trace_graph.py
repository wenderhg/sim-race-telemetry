from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt, QTimer
from collections import deque

class TraceGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(10)
        self.setMinimumHeight(10)
        self.setStyleSheet("background-color: transparent;")
        
        # History size: 60Hz * 5 seconds = 300 points
        self.history_len = 300
        self.throttle_hist = deque([0.0]*self.history_len, maxlen=self.history_len)
        self.brake_hist = deque([0.0]*self.history_len, maxlen=self.history_len)

    def update_data(self, throttle: float, brake: float):
        self.throttle_hist.append(throttle)
        self.brake_hist.append(brake)
        self.update() # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Draw Background
        painter.fillRect(0, 0, w, h, QColor(20, 20, 20, 220))
        
        # Draw Grid Lines
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawLine(0, h * 0.25, w, h * 0.25)
        painter.drawLine(0, h * 0.50, w, h * 0.50)
        painter.drawLine(0, h * 0.75, w, h * 0.75)

        # Helper to map data index to x coordinate
        # Newest data at right (w), oldest at left (0)
        step_x = w / (self.history_len - 1) if self.history_len > 1 else 0

        # Draw Throttle (Green)
        path_t = QPainterPath()
        first = True
        for i, val in enumerate(self.throttle_hist):
            x = i * step_x
            y = h - (val * h)
            if first:
                path_t.moveTo(x, y)
                first = False
            else:
                path_t.lineTo(x, y)
        
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawPath(path_t)

        # Draw Brake (Red)
        path_b = QPainterPath()
        first = True
        for i, val in enumerate(self.brake_hist):
            x = i * step_x
            y = h - (val * h)
            if first:
                path_b.moveTo(x, y)
                first = False
            else:
                path_b.lineTo(x, y)
        
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawPath(path_b)
