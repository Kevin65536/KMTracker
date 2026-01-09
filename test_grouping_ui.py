"""
Quick test script for the App Grouping UI.
"""
import sys
from PySide6.QtWidgets import QApplication
from src.config import Config
from src.database import Database
from src.ui.app_grouping import AppGroupingDialog

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Initialize config and database
    config = Config()
    database = Database()
    
    # Create and show the dialog
    dialog = AppGroupingDialog(config, database)
    dialog.show()
    
    sys.exit(app.exec())
