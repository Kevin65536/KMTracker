from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QColor, QPainter

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput |
            Qt.WindowDoesNotAcceptFocus  # Prevent focus stealing
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        # Prevent Windows from detecting this as a fullscreen app
        self.setAttribute(Qt.WA_X11NetWmWindowTypeNotification, True)
        
        # Use a small fixed size for the combo counter area instead of full screen
        # This prevents Windows from treating it as a fullscreen overlay
        self.setFixedSize(250, 100)
        
        # Position in top right corner
        screen_geo = QApplication.primaryScreen().geometry()
        self.move(screen_geo.width() - 270, 50)
        
        self.combo_count = 0
        self.combo_label = QLabel(self)
        self.combo_label.setAlignment(Qt.AlignCenter)
        self.combo_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.combo_label.setStyleSheet("color: #00FF00; background-color: transparent;")
        self.combo_label.hide()
        
        # Fill the widget
        self.combo_label.resize(250, 100)
        self.combo_label.move(0, 0)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_combo)
        self.timer.setSingleShot(True)
        
        self.shake_anim = QPropertyAnimation(self, b"pos")  # Animate the window itself
        self.shake_anim.setDuration(100)
        self.shake_anim.setEasingCurve(QEasingCurve.InOutBounce)

    def on_key_press(self):
        self.combo_count += 1
        self.combo_label.setText(f"{self.combo_count} COMBO!")
        self.combo_label.show()
        self.combo_label.adjustSize()
        
        # Reset timer
        self.timer.start(2000) # 2 seconds to keep combo
        
        # Shake effect - animate the window position
        screen_geo = QApplication.primaryScreen().geometry()
        base_pos = QPoint(screen_geo.width() - 270, 50)
        self.shake_anim.stop()
        self.shake_anim.setStartValue(base_pos)
        self.shake_anim.setKeyValueAt(0.25, base_pos + QPoint(5, 0))
        self.shake_anim.setKeyValueAt(0.5, base_pos - QPoint(5, 0))
        self.shake_anim.setKeyValueAt(0.75, base_pos + QPoint(3, 0))
        self.shake_anim.setEndValue(base_pos)
        self.shake_anim.start()

    def reset_combo(self):
        self.combo_count = 0
        self.combo_label.hide()
