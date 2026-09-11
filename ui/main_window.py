"""Main application window"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QStatusBar
)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    """Main window for CNC Controller application"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('CNC Controller')
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Add tabs
        tabs.addTab(self.create_control_tab(), "Управление")
        tabs.addTab(self.create_monitor_tab(), "Мониторинг")
        tabs.addTab(self.create_settings_tab(), "Настройки")

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Готово')

    def create_control_tab(self):
        """Create control tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Управление станком'))
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_monitor_tab(self):
        """Create monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Мониторинг состояния'))
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Настройки приложения'))
        layout.addStretch()
        widget.setLayout(layout)
        return widget
