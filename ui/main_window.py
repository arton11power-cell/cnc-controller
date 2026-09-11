"""Main application window for 5-axis CNC Controller"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QStatusBar,
    QMessageBox, QProgressBar, QSpinBox, QDoubleSpinBox,
    QComboBox, QFileDialog, QTextEdit, QGroupBox,
    QGridLayout, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QFont, QColor
import os
from core.machine_controller import MachineController
from ui.widgets.control_widget import ControlWidget
from ui.widgets.monitor_widget import MonitorWidget
from ui.widgets.gcode_widget import GCodeWidget


class MainWindow(QMainWindow):
    """Main window for CNC Controller application"""

    def __init__(self):
        super().__init__()
        self.controller = MachineController()
        self.init_ui()
        self.setup_connections()
        self.start_monitor_timer()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('CNC 5-Axis Controller')
        self.setGeometry(100, 50, 1400, 900)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Create tab widgets
        self.control_widget = ControlWidget(self.controller)
        self.monitor_widget = MonitorWidget(self.controller)
        self.gcode_widget = GCodeWidget(self.controller)
        settings_widget = self.create_settings_tab()

        # Add tabs
        tabs.addTab(self.control_widget, "🎮 Управление")
        tabs.addTab(self.monitor_widget, "📊 Мониторинг")
        tabs.addTab(self.gcode_widget, "📄 G-код")
        tabs.addTab(settings_widget, "⚙️ Настройки")

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Готово')

    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Serial port settings
        port_group = QGroupBox("Подключение")
        port_layout = QGridLayout()

        port_layout.addWidget(QLabel("COM порт:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', '/dev/ttyUSB0', '/dev/ttyUSB1'])
        port_layout.addWidget(self.port_combo, 0, 1)

        port_layout.addWidget(QLabel("Скорость (baud):"), 1, 0)
        self.baud_spin = QSpinBox()
        self.baud_spin.setRange(9600, 921600)
        self.baud_spin.setValue(115200)
        port_layout.addWidget(self.baud_spin, 1, 1)

        connect_btn = QPushButton("Подключиться")
        connect_btn.clicked.connect(self.connect_to_device)
        port_layout.addWidget(connect_btn, 2, 0, 1, 2)

        self.connection_status = QLabel("❌ Отключено")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        port_layout.addWidget(self.connection_status, 3, 0, 1, 2)

        port_group.setLayout(port_layout)
        layout.addWidget(port_group)

        # Machine settings
        machine_group = QGroupBox("Параметры станка")
        machine_layout = QGridLayout()

        machine_layout.addWidget(QLabel("Шагов/мм (X, Y, Z):"), 0, 0)
        self.steps_per_mm_spin = QDoubleSpinBox()
        self.steps_per_mm_spin.setValue(800.0)
        machine_layout.addWidget(self.steps_per_mm_spin, 0, 1)

        machine_layout.addWidget(QLabel("Макс. скорость (мм/мин):"), 1, 0)
        self.max_speed_spin = QSpinBox()
        self.max_speed_spin.setRange(100, 10000)
        self.max_speed_spin.setValue(5000)
        machine_layout.addWidget(self.max_speed_spin, 1, 1)

        machine_layout.addWidget(QLabel("Ускорение (мм/с²):"), 2, 0)
        self.accel_spin = QDoubleSpinBox()
        self.accel_spin.setValue(100.0)
        machine_layout.addWidget(self.accel_spin, 2, 1)

        machine_group.setLayout(machine_layout)
        layout.addWidget(machine_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def start_monitor_timer(self):
        """Start monitor update timer"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_status)
        self.monitor_timer.start(100)  # Update every 100ms

    def update_status(self):
        """Update status bar and monitor"""
        status = self.controller.get_status()
        if status:
            self.status_bar.showMessage(
                f"X:{status['pos_x']:.2f} Y:{status['pos_y']:.2f} Z:{status['pos_z']:.2f} "
                f"A:{status['pos_a']:.2f} B:{status['pos_b']:.2f}"
            )

    def connect_to_device(self):
        """Connect to STM32 device"""
        port = self.port_combo.currentText()
        baudrate = self.baud_spin.value()

        try:
            if self.controller.connect(port, baudrate):
                self.connection_status.setText("✓ Подключено")
                self.connection_status.setStyleSheet("color: green; font-weight: bold;")
                QMessageBox.information(self, "Успех", f"Подключено к {port}")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось подключиться к {port}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def closeEvent(self, event):
        """Handle window close event"""
        if self.controller.is_connected():
            reply = QMessageBox.question(
                self,
                "Выход",
                "Отключить станок перед выходом?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.controller.disconnect()
        event.accept()
