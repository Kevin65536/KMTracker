"""
Application Grouping Dialog for ActivityTrack.
Allows users to categorize applications into productivity and other groups.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QSplitter,
    QAbstractItemView, QWidget, QMessageBox, QLineEdit, QFileIconProvider
)
from PySide6.QtCore import Qt, Signal, QFileInfo
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent

from ..i18n import tr
from ..config import Config


class AppGroupingDialog(QDialog):
    """Dialog for managing application groups (productivity vs other)."""
    
    # Signal emitted when groups are changed
    groups_changed = Signal()
    
    def __init__(self, config: Config, database=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.database = database
        self.metadata = {}
        self.icon_provider = QFileIconProvider()
        self.setWindowTitle(tr('grouping.title'))
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_data()
        self.apply_dark_style()
    
    def apply_dark_style(self):
        """Apply dark theme styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QGroupBox {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                padding-top: 12px;
                font-size: 14px;
                font-weight: bold;
                color: #00e676;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 0px;
                padding: 2px 8px;
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 3px;
                margin: 2px;
                min-height: 24px;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #00e676;
                color: #1e1e1e;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2b2b2b;
            }
            QPushButton#productivityBtn {
                background-color: #00897b;
            }
            QPushButton#productivityBtn:hover {
                background-color: #00a089;
            }
            QPushButton#otherBtn {
                background-color: #f57c00;
            }
            QPushButton#otherBtn:hover {
                background-color: #ff9100;
            }
            QPushButton#unassignBtn {
                background-color: #616161;
            }
            QPushButton#unassignBtn:hover {
                background-color: #757575;
            }
            QPushButton#saveBtn {
                background-color: #00e676;
                color: #1e1e1e;
            }
            QPushButton#saveBtn:hover {
                background-color: #00c853;
            }
            QPushButton#cancelBtn {
                background-color: #c62828;
                color: #ffffff;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e53935;
            }
            QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #00e676;
            }
            QSplitter::handle {
                background-color: #3d3d3d;
            }
        """)
    
    def setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel(tr('grouping.title'))
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        main_layout.addWidget(title_label)
        
        desc_label = QLabel(tr('grouping.description'))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888888; font-size: 13px;")
        main_layout.addWidget(desc_label)
        
        # Search filter
        search_layout = QHBoxLayout()
        search_label = QLabel(tr('grouping.search'))
        search_label.setStyleSheet("color: #ffffff; font-size: 13px;")
        search_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr('grouping.search_placeholder'))
        self.search_edit.textChanged.connect(self.filter_apps)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)
        
        # Main content with three lists
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Unassigned apps list
        unassigned_group = QGroupBox(tr('grouping.unassigned'))
        unassigned_layout = QVBoxLayout(unassigned_group)
        self.unassigned_list = QListWidget()
        self.unassigned_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        unassigned_layout.addWidget(self.unassigned_list)
        content_layout.addWidget(unassigned_group, 1)
        
        # Center buttons for moving apps
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        
        self.to_productivity_btn = QPushButton("→ " + tr('grouping.to_productivity'))
        self.to_productivity_btn.setObjectName("productivityBtn")
        self.to_productivity_btn.clicked.connect(self.move_to_productivity)
        center_layout.addWidget(self.to_productivity_btn)
        
        self.to_other_btn = QPushButton("→ " + tr('grouping.to_other'))
        self.to_other_btn.setObjectName("otherBtn")
        self.to_other_btn.clicked.connect(self.move_to_other)
        center_layout.addWidget(self.to_other_btn)
        
        center_layout.addSpacing(20)
        
        self.unassign_btn = QPushButton("← " + tr('grouping.unassign'))
        self.unassign_btn.setObjectName("unassignBtn")
        self.unassign_btn.clicked.connect(self.move_to_unassigned)
        center_layout.addWidget(self.unassign_btn)
        
        center_layout.addStretch()
        content_layout.addLayout(center_layout)
        
        # Right side: Productivity and Other groups stacked
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        
        # Productivity apps list
        productivity_group = QGroupBox(tr('grouping.productivity'))
        productivity_layout = QVBoxLayout(productivity_group)
        self.productivity_list = QListWidget()
        self.productivity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        productivity_layout.addWidget(self.productivity_list)
        right_layout.addWidget(productivity_group, 1)
        
        # Other apps list
        other_group = QGroupBox(tr('grouping.other'))
        other_layout = QVBoxLayout(other_group)
        self.other_list = QListWidget()
        self.other_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        other_layout.addWidget(self.other_list)
        right_layout.addWidget(other_group, 1)
        
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #888888; font-size: 12px;")
        main_layout.addWidget(self.stats_label)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton(tr('grouping.cancel'))
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton(tr('grouping.save'))
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self.save_and_close)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_data(self):
        """Load all apps and their current groupings."""
        # Get all apps from database
        all_apps = []
        if self.database:
            all_apps = self.database.get_all_apps()
            # Get metadata for friendly names and icons
            self.metadata = self.database.get_app_metadata_dict()
        
        # Get current groupings from config
        groups = self.config.app_groups
        productivity_apps = set(groups.get('productivity', []))
        other_apps = set(groups.get('other', []))
        
        # Categorize apps
        for app_name in all_apps:
            if app_name in productivity_apps:
                self._add_app_item(self.productivity_list, app_name)
            elif app_name in other_apps:
                self._add_app_item(self.other_list, app_name)
            else:
                self._add_app_item(self.unassigned_list, app_name)
        
        # Add any apps in config that aren't in the database
        for app_name in productivity_apps:
            if app_name not in all_apps:
                self._add_app_item(self.productivity_list, app_name)
        
        for app_name in other_apps:
            if app_name not in all_apps:
                self._add_app_item(self.other_list, app_name)
        
        # Sort all lists
        self.unassigned_list.sortItems()
        self.productivity_list.sortItems()
        self.other_list.sortItems()
        
        self.update_stats()
    
    def _add_app_item(self, list_widget, app_name):
        """Add an app item with icon and friendly name to the list."""
        # Get friendly name and icon
        friendly_name = app_name
        exe_path = None
        
        if app_name in self.metadata:
            meta = self.metadata[app_name]
            friendly_name = meta.get('friendly_name') or app_name
            exe_path = meta.get('exe_path')
        
        # Create item
        item = QListWidgetItem(friendly_name)
        
        # Set icon if available
        if exe_path:
            info = QFileInfo(exe_path)
            icon = self.icon_provider.icon(info)
            if not icon.isNull():
                item.setIcon(icon)
        
        # Store the real app name as user data for saving
        item.setData(Qt.UserRole, app_name)
        # Set tooltip to show real exe name
        item.setToolTip(app_name)
        
        list_widget.addItem(item)
    
    def filter_apps(self, text):
        """Filter apps in all lists based on search text."""
        text = text.lower()
        
        for list_widget in [self.unassigned_list, self.productivity_list, self.other_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                # Search in both display text and real app name
                real_name = item.data(Qt.UserRole) or item.text()
                item.setHidden(text not in item.text().lower() and text not in real_name.lower())
    
    def move_to_productivity(self):
        """Move selected apps from unassigned to productivity."""
        selected = self.unassigned_list.selectedItems()
        for item in selected:
            app_name = item.data(Qt.UserRole) or item.text()
            self.unassigned_list.takeItem(self.unassigned_list.row(item))
            self._add_app_item(self.productivity_list, app_name)
        self.productivity_list.sortItems()
        self.update_stats()
    
    def move_to_other(self):
        """Move selected apps from unassigned to other."""
        selected = self.unassigned_list.selectedItems()
        for item in selected:
            app_name = item.data(Qt.UserRole) or item.text()
            self.unassigned_list.takeItem(self.unassigned_list.row(item))
            self._add_app_item(self.other_list, app_name)
        self.other_list.sortItems()
        self.update_stats()
    
    def move_to_unassigned(self):
        """Move selected apps from productivity/other back to unassigned."""
        # From productivity
        for item in self.productivity_list.selectedItems():
            app_name = item.data(Qt.UserRole) or item.text()
            self.productivity_list.takeItem(self.productivity_list.row(item))
            self._add_app_item(self.unassigned_list, app_name)
        
        # From other
        for item in self.other_list.selectedItems():
            app_name = item.data(Qt.UserRole) or item.text()
            self.other_list.takeItem(self.other_list.row(item))
            self._add_app_item(self.unassigned_list, app_name)
        
        self.unassigned_list.sortItems()
        self.update_stats()
    
    def update_stats(self):
        """Update the stats label showing counts."""
        unassigned = self.unassigned_list.count()
        productivity = self.productivity_list.count()
        other = self.other_list.count()
        total = unassigned + productivity + other
        
        self.stats_label.setText(
            tr('grouping.stats', 
               total=total, 
               productivity=productivity, 
               other=other, 
               unassigned=unassigned)
        )
    
    def save_and_close(self):
        """Save the groupings and close the dialog."""
        # Collect apps from each list using real app names
        productivity_apps = []
        for i in range(self.productivity_list.count()):
            item = self.productivity_list.item(i)
            app_name = item.data(Qt.UserRole) or item.text()
            productivity_apps.append(app_name)
        
        other_apps = []
        for i in range(self.other_list.count()):
            item = self.other_list.item(i)
            app_name = item.data(Qt.UserRole) or item.text()
            other_apps.append(app_name)
        
        # Save to config
        self.config.app_groups = {
            'productivity': productivity_apps,
            'other': other_apps
        }
        
        self.groups_changed.emit()
        self.accept()
    
    def retranslate_ui(self):
        """Update UI text for current language."""
        self.setWindowTitle(tr('grouping.title'))
        # Update other labels as needed
