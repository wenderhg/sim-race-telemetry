from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class VerticalBar(QWidget):
    def __init__(self, name, color, initial_val=0):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)
        
        self.color = color
        self.label = QLabel("0")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-weight: bold; font-size: 10px;")
        
        self.bar = QProgressBar()
        self.bar.setOrientation(Qt.Vertical)
        self.bar.setRange(0, 100)
        self.bar.setValue(initial_val)
        self.bar.setTextVisible(False)
        self.update_style(1.0) # Initial style
        
        layout.addWidget(self.label)
        layout.addWidget(self.bar)
        self.setLayout(layout)

    def set_value(self, val_float):
        # val_float 0.0 to 1.0
        val_int = int(val_float * 100)
        self.bar.setValue(val_int)
        self.label.setText(str(val_int))

    def update_style(self, scale):
        width = int(10 * scale)
        font_size = max(6, int(6 * scale)) # Minimum readable font
        
        self.label.setStyleSheet(f"color: white; font-weight: bold; font-size: {font_size}px;")
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #444;
                background-color: #222;
                border-radius: 2px;
                width: {width}px;
            }}
            QProgressBar::chunk {{
                background-color: {self.color};
            }}
        """)

class InputBarsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        self.clutch = VerticalBar("C", "#888888")
        self.brake = VerticalBar("B", "#FF0000")
        self.throttle = VerticalBar("T", "#00FF00")
        
        layout.addWidget(self.clutch)
        layout.addWidget(self.brake)
        layout.addWidget(self.throttle)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgba(0,0,0,200); border-radius: 5px;")

    def update_data(self, clutch, brake, throttle):
        self.clutch.set_value(clutch)
        self.brake.set_value(brake)
        self.throttle.set_value(throttle)

    def set_scale(self, scale):
        self.clutch.update_style(scale)
        self.brake.update_style(scale)
        self.throttle.update_style(scale)
