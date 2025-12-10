import sys
import signal
import os
import faulthandler
import traceback
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.tracker import InputTracker
from src.ui.main_window import MainWindow
from src.ui.tray_icon import TrayIcon
from src.config import Config

def main():
    # Crash/exception diagnostics: dump tracebacks on fatal errors and uncaught exceptions
    # Note: faulthandler requires sys.stderr, which is None when console=False in PyInstaller
    if sys.stderr is not None:
        try:
            faulthandler.enable(all_threads=True)
        except Exception:
            pass  # Silently ignore if faulthandler fails

    def log_exception(exc_type, exc_value, exc_tb):
        # When packaged without console, stderr might be None
        if sys.stderr is not None:
            print("[FATAL] Unhandled exception:", exc_type.__name__, exc_value, file=sys.stderr)
            traceback.print_exception(exc_type, exc_value, exc_tb)

    sys.excepthook = log_exception

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    skip_tracker = os.environ.get("SKIP_TRACKER", "0") == "1"
    if skip_tracker:
        print("[WARN] SKIP_TRACKER=1 -> tracker is DISABLED for diagnostics")
        tracker = InputTracker()
    else:
        tracker = InputTracker()
        tracker.start()
    
    # Initialize config
    config = Config()
    
    # Initialize UI
    window = MainWindow(tracker, config)
    tray = TrayIcon()
    
    # Connect signals
    tray.show_window_signal.connect(window.show)
    tray.show_window_signal.connect(window.activateWindow)
    
    def quit_app():
        if not skip_tracker:
            tracker.stop()
        app.quit()
        
    tray.quit_signal.connect(quit_app)
    
    # Show window initially
    window.show()
    
    # Allow python to handle signals by letting the event loop wake up periodically
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
