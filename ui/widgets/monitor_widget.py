"""Monitor widget for real-time machine status"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QGridLayout, QProgressBar, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class MonitorWidget(QWidget):
    """Widget for monitoring machine status"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize monitor widget UI"""
        main_layout = QVBoxLayout()

        # Position display
        pos_group = QGroupBox("Текущее положение")
        pos_layout = QGridLayout()

        self.position_labels = {}
        axes = ['X', 'Y', 'Z', 'A', 'B']

        for i, axis in enumerate(axes):
            pos_layout.addWidget(QLabel(f"{axis}:"), i, 0)
            label = QLabel("0.00")
            label.setStyleSheet("font-weight: bold; font-size: 14px;")
            pos_layout.addWidget(label, i, 1)
            self.position_labels[axis] = label

        pos_group.setLayout(pos_layout)
        main_layout.addWidget(pos_group)

        # Status display
        status_group = QGroupBox("Статус системы")
        status_layout = QGridLayout()

        self.status_labels = {}
        statuses = [
            ('Motor X', '❌ Стоп'),
            ('Motor Y', '❌ Стоп'),
            ('Motor Z', '❌ Стоп'),
            ('Motor A', '❌ Стоп'),
            ('Motor B', '❌ Стоп'),
            ('Spindle', '⭕ Выключен'),
            ('Cooling', '⭕ Выключен'),
            ('Connection', '🔴 Отключено')
        ]

        for i, (name, status) in enumerate(statuses):
            status_layout.addWidget(QLabel(f"{name}:"), i // 4, (i % 4) * 2)
            label = QLabel(status)
            label.setStyleSheet("font-weight: bold;")
            status_layout.addWidget(label, i // 4, (i % 4) * 2 + 1)
            self.status_labels[name] = label

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # Sensor status table
        sensor_group = QGroupBox("Датчики (Эндстопы)")
        sensor_layout = QVBoxLayout()

        self.sensor_table = QTableWidget()
        self.sensor_table.setColumnCount(2)
        self.sensor_table.setHorizontalHeaderLabels(['Датчик', 'Статус'])
        self.sensor_table.setRowCount(5)

        sensors = ['X-endstop', 'Y-endstop', 'Z-endstop', 'A-endstop', 'B-endstop']
        for i, sensor in enumerate(sensors):
            self.sensor_table.setItem(i, 0, QTableWidgetItem(sensor))
            self.sensor_table.setItem(i, 1, QTableWidgetItem("✓ OK"))

        sensor_layout.addWidget(self.sensor_table)
        sensor_group.setLayout(sensor_layout)
        main_layout.addWidget(sensor_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def update_position(self, positions):
        """Update axis positions"""
        for axis, pos in positions.items():
            if axis in self.position_labels:
                self.position_labels[axis].setText(f"{pos:.2f}")

    def update_status(self, status):
        """Update system status"""
        for name, value in status.items():
            if name in self.status_labels:
                self.status_labels[name].setText(value)
