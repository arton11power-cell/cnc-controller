"""Control widget for manual machine control"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QGridLayout, QSpinBox, QDoubleSpinBox, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor


class ControlWidget(QWidget):
    """Widget for manual control of 5-axis machine"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize control widget UI"""
        main_layout = QVBoxLayout()

        # Axis control section
        axis_group = QGroupBox("Управление осями")
        axis_layout = QGridLayout()

        # Create controls for each axis (X, Y, Z, A, B)
        self.axis_controls = {}
        axes_info = [
            ('X', 'Линейная ось X (мм)'),
            ('Y', 'Линейная ось Y (мм)'),
            ('Z', 'Линейная ось Z (мм)'),
            ('A', 'Ротационная ось A (°)'),
            ('B', 'Ротационная ось B (°)')
        ]

        for row, (axis, description) in enumerate(axes_info):
            axis_layout.addWidget(QLabel(f"{axis}:"), row, 0)
            axis_layout.addWidget(QLabel(description), row, 1)

            # Distance spinbox
            dist_spin = QDoubleSpinBox()
            dist_spin.setRange(-1000, 1000)
            dist_spin.setValue(0)
            dist_spin.setSingleStep(0.1)
            axis_layout.addWidget(dist_spin, row, 2)

            # Speed spinbox
            speed_spin = QSpinBox()
            speed_spin.setRange(1, 10000)
            speed_spin.setValue(100)
            axis_layout.addWidget(speed_spin, row, 3)

            # Move button
            move_btn = QPushButton(f"Переместить {axis}")
            move_btn.clicked.connect(
                lambda checked, a=axis, d=dist_spin, s=speed_spin: self.move_axis(a, d, s)
            )
            axis_layout.addWidget(move_btn, row, 4)

            self.axis_controls[axis] = {
                'distance': dist_spin,
                'speed': speed_spin,
                'button': move_btn
            }

        axis_group.setLayout(axis_layout)
        main_layout.addWidget(axis_group)

        # Quick movement buttons
        quick_group = QGroupBox("Быстрые команды")
        quick_layout = QHBoxLayout()

        home_btn = QPushButton("На ноль (Home)")
        home_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        home_btn.clicked.connect(self.home_machine)
        quick_layout.addWidget(home_btn)

        emergency_btn = QPushButton("СТОП (Emergency)")
        emergency_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        emergency_btn.clicked.connect(self.emergency_stop)
        quick_layout.addWidget(emergency_btn)

        enable_btn = QPushButton("Включить двигатели")
        enable_btn.setStyleSheet("background-color: #2196F3; color: white;")
        enable_btn.clicked.connect(self.enable_motors)
        quick_layout.addWidget(enable_btn)

        disable_btn = QPushButton("Отключить двигатели")
        disable_btn.setStyleSheet("background-color: #FF9800; color: white;")
        disable_btn.clicked.connect(self.disable_motors)
        quick_layout.addWidget(disable_btn)

        quick_group.setLayout(quick_layout)
        main_layout.addWidget(quick_group)

        # Spindle control
        spindle_group = QGroupBox("Управление шпинделем")
        spindle_layout = QHBoxLayout()

        spindle_layout.addWidget(QLabel("Скорость шпинделя (об/мин):"))
        self.spindle_speed = QSpinBox()
        self.spindle_speed.setRange(0, 24000)
        self.spindle_speed.setValue(0)
        spindle_layout.addWidget(self.spindle_speed)

        spindle_on_btn = QPushButton("Включить шпиндель")
        spindle_on_btn.setStyleSheet("background-color: #9C27B0; color: white;")
        spindle_on_btn.clicked.connect(self.spindle_on)
        spindle_layout.addWidget(spindle_on_btn)

        spindle_off_btn = QPushButton("Отключить шпиндель")
        spindle_off_btn.setStyleSheet("background-color: #757575; color: white;")
        spindle_off_btn.clicked.connect(self.spindle_off)
        spindle_layout.addWidget(spindle_off_btn)

        spindle_group.setLayout(spindle_layout)
        main_layout.addWidget(spindle_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def move_axis(self, axis, distance_spin, speed_spin):
        """Move specific axis"""
        distance = distance_spin.value()
        speed = speed_spin.value()

        if not self.controller.is_connected():
            QMessageBox.warning(self, "Ошибка", "Станок не подключен!")
            return

        try:
            self.controller.move_axis(axis, distance, speed)
            QMessageBox.information(
                self,
                "Команда отправлена",
                f"Ось {axis}: переместить на {distance} мм/° со скоростью {speed}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def home_machine(self):
        """Move all axes to home position"""
        if not self.controller.is_connected():
            QMessageBox.warning(self, "Ошибка", "Станок не подключен!")
            return

        try:
            self.controller.home_all()
            QMessageBox.information(self, "Успех", "Начинается процесс установки на ноль...")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def emergency_stop(self):
        """Emergency stop"""
        try:
            self.controller.emergency_stop()
            QMessageBox.warning(self, "Стоп!", "Активирована аварийная остановка!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def enable_motors(self):
        """Enable all motors"""
        try:
            self.controller.enable_motors()
            QMessageBox.information(self, "Успех", "Двигатели включены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def disable_motors(self):
        """Disable all motors"""
        try:
            self.controller.disable_motors()
            QMessageBox.information(self, "Успех", "Двигатели отключены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def spindle_on(self):
        """Turn on spindle"""
        speed = self.spindle_speed.value()
        try:
            self.controller.spindle_on(speed)
            QMessageBox.information(self, "Успех", f"Шпиндель включен на {speed} об/мин")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def spindle_off(self):
        """Turn off spindle"""
        try:
            self.controller.spindle_off()
            QMessageBox.information(self, "Успех", "Шпиндель отключен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
